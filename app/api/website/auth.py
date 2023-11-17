from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from cryptography.fernet import Fernet
from ...db.sqldb.services import user_service, cookie_service
from ...services.security import api_key_auth
from fastapi.security.api_key import APIKey
from datetime import datetime, timedelta


router = APIRouter(
    prefix="/auth",
    tags=["website"]
)


@router.post("/login/")
async def login(user_id: int,
                api_key: APIKey = Depends(api_key_auth)) -> dict[str, str]:

    key = Fernet.generate_key()
    cipher_suite = Fernet(key)

    email = user_service.get_by_id(user_id).email

    encrypted_str = cipher_suite.encrypt(email.encode()).decode()
    expiration_time = datetime.utcnow() + timedelta(seconds=3601)
    cookie_service.create({"user_id": user_id, "token": encrypted_str, "expires_at": expiration_time})
    return {"token": encrypted_str}


@router.get("/verify/")
async def verify(token: str = Cookie(None),
                 api_key: APIKey = Depends(api_key_auth)) -> dict[str, str]:
    session_data = cookie_service.get_by_token(token)

    if not session_data:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if session_data.expires_at < datetime.utcnow():
        cookie_service.delete(session_data.id)
        raise HTTPException(status_code=401, detail="Session expired")

    email: str = session_data.user.email

    return {"email": email}
