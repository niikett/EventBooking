from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, status, HTTPException, Query
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app.models import *
from app.schemas import *
from app.core import security
from app.core import jwt_token
from app.core.config_db import get_db

router = APIRouter(
    prefix="/auth", 
    tags=["auth"]
)

#####################################################################################################################################
# sign-in
@router.post(
    "/sign-in",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse
)
def sign_in(
    role: str = Query(...),
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        user_found = db.query(User).filter(User.email == user_credentials.username).first()

        if not user_found:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail={
                    "error":"invalid email or password",
                    # "error":"invalid email",
                    "status_code":status.HTTP_401_UNAUTHORIZED,
                }
            )

        if not security.verify_user(user_credentials.password, user_found.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail={
                    "error":"invalid email or password",
                    # "error":"invalid password",
                    "status_code":status.HTTP_401_UNAUTHORIZED,
                }
            )

        access_token = jwt_token.create_access_token({"id": str(user_found.id)})

        return TokenResponse(
            access_token=access_token, 
            token_type="bearer", 
            user=UserResponse(
                **user_found.__dict__,
            ),
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": str(e),
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
            }
        ) 
#####################################################################################################################################
# sign-up
@router.post(
    "/sign-up", 
    status_code=status.HTTP_201_CREATED, 
)
def sign_up(
    user_details: UserCreate, 
    db: Session = Depends(get_db)
):
    try: 
        existing_user = db.query(User).filter(User.email == user_details.email).first()
    
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail={
                    "error": "account can't create with these email id",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                }
            )
        
        hashed_password = security.hash_password(user_details.password)

        created_user = User(**user_details.model_dump())
        created_user.name = user_details.name.title() 
        created_user.password = hashed_password 

        db.add(created_user)
        db.flush()
        db.refresh(created_user)

        response_data = {
            "status_code":status.HTTP_201_CREATED
        }

        db.commit()

        return response_data
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": str(e),
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
            }
        )
#####################################################################################################################################
