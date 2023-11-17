from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from typing import Optional
from ...services.security import api_key_auth
from ...db.sqldb.services import contact_service
from fastapi.security.api_key import APIKey
import requests
import traceback


router = APIRouter(
    prefix="/contact",
    tags=["website"]
)


@router.post("/", status_code=status.HTTP_200_OK)
async def submit_contact_form(name: str, email: str, message: str,
                              api_key: APIKey = Depends(api_key_auth)) -> int:
    contact_id = contact_service.create({"name": name, "email": email,
                                         "message": message})
    return contact_id
