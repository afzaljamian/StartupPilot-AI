from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from ..config import settings

client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
db = client[settings.mongodb_db]
users = db.users
runs = db.runs
reports = db.reports

def oid(value: str):
    try: return ObjectId(value)
    except Exception: return None

async def init_db():
    await users.create_index('email', unique=True)
    await runs.create_index([('user_id', 1), ('created_at', -1)])
    await reports.create_index('run_id', unique=True)

async def get_user_by_email(email: str):
    return await users.find_one({'email': email.lower()})

async def get_user_by_id(user_id: str):
    doc = await users.find_one({'_id': oid(user_id)})
    if not doc: return None
    doc['id'] = str(doc.pop('_id'))
    return doc

async def create_user(name: str, email: str, password_hash: str):
    now = datetime.now(timezone.utc)
    result = await users.insert_one({'name': name, 'email': email.lower(), 'password_hash': password_hash, 'created_at': now})
    return {'id': str(result.inserted_id), 'name': name, 'email': email.lower(), 'created_at': now}

async def create_run(user_id: str, payload: dict):
    now = datetime.now(timezone.utc)
    doc = {'user_id': oid(user_id), **payload, 'status': 'queued', 'created_at': now, 'completed_at': None, 'error': None}
    result = await runs.insert_one(doc)
    return str(result.inserted_id)

async def update_run(run_id: str, **updates):
    await runs.update_one({'_id': oid(run_id)}, {'$set': updates})

async def get_run(run_id: str, user_id: str | None = None):
    query = {'_id': oid(run_id)}
    if user_id: query['user_id'] = oid(user_id)
    doc = await runs.find_one(query)
    if doc: doc['run_id'] = str(doc.pop('_id'))
    return doc

async def list_runs(user_id: str):
    cursor = runs.find({'user_id': oid(user_id)}).sort('created_at', -1)
    out=[]
    async for doc in cursor:
        doc['run_id'] = str(doc.pop('_id'))
        if doc.get('user_id') is not None:
            doc['user_id'] = str(doc['user_id'])
        out.append(doc)
    return out

async def delete_run(run_id: str, user_id: str):
    await reports.delete_one({'run_id': run_id})
    return await runs.delete_one({'_id': oid(run_id), 'user_id': oid(user_id)})

async def save_report(run_id: str, report: dict):
    await reports.replace_one({'run_id': run_id}, {'run_id': run_id, **report}, upsert=True)

async def get_report(run_id: str):
    doc = await reports.find_one({'run_id': run_id}, {'_id': 0})
    return doc
