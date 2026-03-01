from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.app.api.schemas.user import UserRead
from src.app.security import validate_token
from src.app.db.session import get_db
from src.app.db.models.user import User

security = HTTPBearer()

def decode_token(token: str, expecting_type: str):
    try:
        payload = validate_token(token)

        if payload["type"] != expecting_type:
            raise HTTPException(status_code=401, detail=f"Expected \"{expecting_type}\" token, found \"{payload["type"]}\"")

        return payload
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail=str(e))

def token_get_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserRead:
    payload = decode_token(token.credentials)
    
    user = db.query(User).filter(User.id == payload["uuid"]).first()
    if user == None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return UserRead.model_validate(user)
