import os
from fastapi import HTTPException, status, Security
from .oauth import api_key_header, api_key_cookie

API_KEY = os.getenv("GAMBRINUS_API_KEY")


async def api_key_auth(
        api_key_header: str = Security(api_key_header),
        api_key_cookie: str = Security(api_key_cookie),
):
    if api_key_header == API_KEY:
        return api_key_header
    elif api_key_cookie == API_KEY:
        return api_key_cookie
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )