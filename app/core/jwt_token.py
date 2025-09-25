import copy
from uuid import UUID
from datetime import datetime, timedelta

from jose import jwt, JWTError

from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from app.models import *
from app.schemas import *
from app.core import config_db
from app.core.config import settings


oauth_scheme = OAuth2PasswordBearer(tokenUrl="login")


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_TIME = settings.access_token_expire_time


def create_access_token(
    data: dict
):
    to_encode = copy.deepcopy(data)
    
    for key, value in to_encode.items():
        if isinstance(value, UUID):
            to_encode[key] = str(value)
            
    expire = datetime.utcnow() + timedelta(seconds=ACCESS_TOKEN_EXPIRE_TIME)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_access_token(
    token: str, 
    credentials_exception
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        id = payload.get("id")
        
        if id is None:
            raise credentials_exception
        token_data = TokenData(token_id=id)
    except JWTError:
        raise credentials_exception
    
    return token_data

    
def get_current_user(
    token: str = Depends(oauth_scheme), 
    db: Session = Depends(config_db.get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="not valid credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    token_data = verify_access_token(token, credentials_exception)

    user = db.query(User).filter(User.id == token_data.token_id).first()
       
    if user is None:
        raise credentials_exception

    return user

