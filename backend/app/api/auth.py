from fastapi import APIRouter, HTTPException, Depends
from ..schemas.models import UserRegister, UserLogin, TokenResponse, UserOut
from ..database.mongodb import get_user_by_email, create_user
from ..utils.auth import hash_password, verify_password, create_access_token, get_current_user
router=APIRouter(prefix='/api/auth',tags=['auth'])
@router.post('/register',response_model=TokenResponse)
async def register(data: UserRegister):
    if await get_user_by_email(data.email): raise HTTPException(409,'Email already registered')
    user=await create_user(data.name,data.email,hash_password(data.password))
    return TokenResponse(access_token=create_access_token(user['id']),user=UserOut(**user))
@router.post('/login',response_model=TokenResponse)
async def login(data: UserLogin):
    user=await get_user_by_email(data.email)
    if not user or not verify_password(data.password,user['password_hash']): raise HTTPException(401,'Invalid email or password')
    user_out={'id':str(user['_id']),'name':user['name'],'email':user['email'],'created_at':user['created_at']}
    return TokenResponse(access_token=create_access_token(user_out['id']),user=UserOut(**user_out))
@router.get('/me',response_model=UserOut)
async def me(user=Depends(get_current_user)): return UserOut(**user)
