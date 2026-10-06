from fastapi import APIRouter, Depends, HTTPException
from ..schemas.models import RunCreate, RunOut
from ..database.mongodb import create_run,get_run,list_runs,delete_run
from ..utils.auth import get_current_user
from ..tasks.celery_tasks import run_analysis
router=APIRouter(prefix='/api',tags=['startup'])
@router.post('/run')
async def start(data: RunCreate,user=Depends(get_current_user)):
    payload=data.model_dump(); rid=await create_run(user['id'],payload)
    try: run_analysis.delay(rid)
    except Exception: raise HTTPException(503,'Background worker is unavailable')
    return {'run_id':rid,'status':'queued'}
@router.get('/run/{run_id}',response_model=RunOut)
async def get_one(run_id,user=Depends(get_current_user)):
    r=await get_run(run_id,user['id'])
    if not r: raise HTTPException(404,'Run not found')
    return RunOut(**r)
@router.get('/runs')
async def get_all(user=Depends(get_current_user)): return await list_runs(user['id'])
@router.delete('/run/{run_id}')
async def remove(run_id,user=Depends(get_current_user)):
    result=await delete_run(run_id,user['id'])
    if not result.deleted_count: raise HTTPException(404,'Run not found')
    return {'deleted':True}
