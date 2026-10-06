import asyncio, json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as aioredis
from .config import settings
from jose import jwt, JWTError
from .database.mongodb import init_db
from .api import auth,startup,reports,users

app=FastAPI(title='StartupPilot AI API',version='1.0.0',description='Multi-agent startup business planning API')
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_list,allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.include_router(auth.router); app.include_router(startup.router); app.include_router(reports.router); app.include_router(users.router)

@app.on_event('startup')
async def startup_event():
    try: await init_db()
    except Exception: pass

@app.get('/api/health')
async def health():
    return {'status':'ok','demo_mode':settings.demo_mode and not bool(settings.gemini_api_key)}

@app.websocket('/ws/{run_id}')
async def ws_run(websocket: WebSocket, run_id: str, token: str | None = Query(default=None)):
    # Authorization is checked by requiring a valid JWT query token. Frontend receives it from login.
    if not token:
        await websocket.close(code=1008); return
    try:
        payload=jwt.decode(token,settings.jwt_secret,algorithms=[settings.jwt_algorithm])
        if not payload.get('sub'): raise JWTError()
    except JWTError:
        await websocket.close(code=1008); return
    await websocket.accept()
    client=aioredis.from_url(settings.redis_url,decode_responses=True)
    pubsub=client.pubsub(); await pubsub.subscribe(f'startuppilot:run:{run_id}')
    try:
        await websocket.send_json({'type':'connected','run_id':run_id})
        while True:
            msg=await pubsub.get_message(ignore_subscribe_messages=True,timeout=20)
            if msg and msg.get('data'):
                await websocket.send_json(json.loads(msg['data']))
            else:
                await websocket.send_json({'type':'heartbeat','run_id':run_id})
            await asyncio.sleep(.1)
    except WebSocketDisconnect: pass
    except Exception: pass
    finally:
        await pubsub.unsubscribe(f'startuppilot:run:{run_id}'); await client.aclose()
