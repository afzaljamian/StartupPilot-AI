from fastapi import APIRouter, Depends
from ..utils.auth import get_current_user
router=APIRouter(prefix='/api/users',tags=['users'])
@router.get('/profile')
async def profile(user=Depends(get_current_user)): return user
