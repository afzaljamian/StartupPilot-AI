from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from ..utils.auth import get_current_user
from ..database.mongodb import get_run,get_report
from ..services.pdf_service import generate_pdf
router=APIRouter(prefix='/api',tags=['reports'])
@router.get('/report/{run_id}')
async def report(run_id,user=Depends(get_current_user)):
    run=await get_run(run_id,user['id']); data=await get_report(run_id)
    if not run or not data: raise HTTPException(404,'Report not found')
    return {'run_id':run_id,**data}
@router.get('/report/{run_id}/pdf')
async def pdf(run_id,user=Depends(get_current_user)):
    run=await get_run(run_id,user['id']); data=await get_report(run_id)
    if not run or not data: raise HTTPException(404,'Report not found')
    try: content=generate_pdf({'run_id':run_id,**data})
    except Exception: raise HTTPException(500,'PDF generation failed')
    return Response(content,media_type='application/pdf',headers={'Content-Disposition':f'attachment; filename=startuppilot-{run_id}.pdf'})
