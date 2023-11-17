from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from ...db.sqldb.services import client_service
from ...services.security import api_key_auth
from .models import Client
from fastapi.security.api_key import APIKey
from pydantic import Field
import traceback

router = APIRouter(
    prefix="/client",
    tags=["website"]
)


@router.get("/{client_id}/", response_model=Client, status_code=status.HTTP_200_OK)
async def get_client(client_id: int,
                      api_key: APIKey = Depends(api_key_auth)) -> Optional[int]:
    """
    Retrieves the client information based on the Client ID.

    - Args:
        - **user_id** (int): The ID of the user.

    - Returns:
        - **Optional[int]**: The ID of the user if the user exists, None otherwise.

    - Raise:
        - **HTTPException 403**: If the API key is invalid.
    """
    case = client_service.get_by_id(client_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Client ID not found.")
    result = client_service.row2dict(case)
    return result


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_client(name: str, description: str = "",
                        logo: Optional[str] = None, phone: Optional[str] = None,
                        api_key: APIKey = Depends(api_key_auth)) -> int:

    client_id: int = client_service.create({'name': name, "description": description,
                           "logo": logo, "phone": phone})
    return client_id


@router.put("/{client_id}/", status_code=status.HTTP_200_OK)
async def modify_client(client_id: int, name: Optional[str] = None,
                        description: Optional[str] = None,
                        logo: Optional[str] = None, phone: Optional[str] = None,
                        api_key: APIKey = Depends(api_key_auth)) -> bool:
    client = client_service.get_by_id(user_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client ID not found.")
    obj = {'id': client_id}
    if name is not None:
        obj['name'] = name
    if description is not None:
        obj['description'] = description
    if logo is not None:
        obj['logo'] = logo
    if phone is not None:
        obj['phone'] = phone
    if client_id is not None:
        obj['client_id'] = client_id
    try:
        client_service.update(obj)
    except Exception:
        print(traceback.print_exc())
        return False
    else:
        return True


@router.delete("/{client_id}/", status_code=status.HTTP_200_OK)
async def delete_client(client_id: int, api_key: APIKey = Depends(api_key_auth)) -> bool:
    """
    Deletes a specific client from the database using the provided client ID.


    - Args:
        - **client_id** (int): The ID of the client to be retrieved.

    - Returns:
        - **bool**: Whether the user has been deleted or not.

    - Raises:
        - **HTTPException**: If the API key is invalid (403) or if the user ID does not exist in the database (404).
    """
    client = client_service.get_by_id(client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client ID not found.")
    result: bool = client_service.delete([client_id])
    return result
