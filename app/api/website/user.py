from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from ...db.sqldb.services import user_service
from ...services.security import api_key_auth
from ...services.integration.close import CloseService
from .models import User
from fastapi.security.api_key import APIKey
import traceback
import os
from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix="/user",
    tags=["website"]
)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user_id(email: str,
                      api_key: APIKey = Depends(api_key_auth)) -> Optional[int]:
    """
    Retrieves the ID of the user based on the given Wix ID.

    - Args:
        - **email** (str): The email of the user.

    - Returns:
        - **Optional[int]**: The ID of the user if the user exists, None otherwise.

    - Raise:
        - **HTTPException 403**: If the API key is invalid.
    """
    # dummy for now
    user = user_service.get_by_email(email)
    if user is None:
        return None
    else:
        return user.id

@router.get("/{user_id}/", response_model=User, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, api_key: APIKey = Depends(api_key_auth)):
    """
    Retrieves the user information based on the User ID.

    - Args:
        - **user_id** (int): The ID of the user.

    - Returns:
        - **Optional[int]**: The ID of the user if the user exists, None otherwise.

    - Raise:
        - **HTTPException 403**: If the API key is invalid.
    """
    user = user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User ID not found.")
    result = user_service.row2dict(user)
    return result


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user_id(email: str, api_key: APIKey = Depends(api_key_auth)) -> bool:
    """
    Create a user in the database, if it does not already exist.

    - Args:
        - **email** (str): The Email of the user.

    - Returns:
        - **bool**: Whether the user has been created (True) or already exists (False)

    - Raise:
        - **HTTPException 403**: If the API key is invalid.
    """
    user = user_service.get_by_email(email)
    if user is None:
        try:
            user_id: int = user_service.create({"email": email})
        # close API only in prod
        except IntegrityError as e:
            # there is already a user
            return False
        else:
            user_service.create_session(user_id, "First Session")
            if os.getenv("GAMBRINUS_ENV") == "prod":
                close_leads = CloseService.search_lead_by_email(email)
                if len(close_leads) == 0:
                    close_result = CloseService.create_lead(email)
                    print(f"Email {email} in Close: {close_result}")
            return True
    else:
        return False


@router.put("/", status_code=status.HTTP_200_OK)
async def modify_user(user_id: int, email: Optional[str] = None,
                      first_name: Optional[str] = None, last_name: Optional[str] = None,
                      photo: Optional[str] = None, title: Optional[str] = None,
                      client_id: Optional[int] = None,
                      api_key: APIKey = Depends(api_key_auth)):
    """
    Modify a user in the database. All arguments except the user_id is optional; if
    not specified, then it is not modified.

    - Args:
        - **user_id** (int): User ID to query.
        - **email** (str): Modify email of the user.
        - **first_name** (str): Modify first name of the user.
        - **last_name** (str): Modify last name of the user.
        - **photo** (str): Modify photo of the user (link to azure blob).
        - **title** (str): Modify title of the user.
        - **client_id** (int): Modify client associated with the user.

    - Returns:
        - **bool**: Whether the user has been created (True) or already exists (False)

    - Raise:
        - **HTTPException**: If the API key is invalid (403) or if the user ID does not exist in the database (404).
    """
    user = user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User ID not found.")
    obj = {'id': user_id}
    if email is not None:
        obj['email'] = email
    if first_name is not None:
        obj['first_name'] = first_name
    if last_name is not None:
        obj['last_name'] = last_name
    if photo is not None:
        obj['photo'] = photo
    if title is not None:
        obj['title'] = title
    if client_id is not None:
        obj['client_id'] = client_id
    try:
        user_service.update(obj)
    except Exception:
        print(traceback.print_exc())
        return False
    else:
        return True


@router.delete("/{user_id}/", status_code=status.HTTP_200_OK)
async def delete_user(user_id: int, api_key: APIKey = Depends(api_key_auth)) -> bool:
    """
    Deletes a specific user from the database using the provided user ID.


    - Args:
        - **user_id** (int): The ID of the user to be retrieved.

    - Returns:
        - **bool**: Whether the user has been deleted or not.

    - Raises:
        - **HTTPException**: If the API key is invalid (403) or if the user ID does not exist in the database (404).
    """
    user = user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User ID not found.")
    result: bool = user_service.delete([user_id])
    return result


@router.get("/{user_id}/permissions/", status_code=status.HTTP_200_OK)
async def get_user_permissions(user_id: int, api_key: APIKey = Depends(api_key_auth)) -> list[int]:
    """
    Retrieves a list of permission IDs associated with a user.

    - Args:
        - **user_id** (int): The ID of the user for whom permissions are to be retrieved.

    - Returns:
        - **list[int]**: A list of permission IDs associated with the user.

    - Raise:
        - **HTTPException**: If the API key is invalid (403) or the user does not exist (404).
    """
    # find user
    user = user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    permissions = user_service.get_permissions(user_id)
    permission_ids: list[int] = [permission.id for permission in permissions]
    return permission_ids


@router.post("/{user_id}/permissions/{permission_id}/", status_code=status.HTTP_201_CREATED)
async def set_user_permission(user_id: int, permission_id: int, api_key: APIKey = Depends(api_key_auth)) -> bool:
    """
    Sets a permission associated with a user.

    - Args:
        - **user_id** (int): The ID of the user for whom the permission is to be set for.
        - **permissionID** (int): The ID of the permission to be set.

    - Returns:
        - **bool**: True if the permission has been created, or False if it already exists.

    - Raise:
        - **HTTPException**: If the API key is invalid (403) or the user does not exist (404).
    """
    user = user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # find permissions to see if permission has been set already
    permissions = user_service.get_permissions(user_id)
    permission_ids = [permission.id for permission in permissions]
    if permission_id in permission_ids:
        return False
    # create permission
    result: bool = user_service.create_permission(user_id, permission_id)
    return result


@router.delete("/{user_id}/permissions/{permission_id}/", status_code=status.HTTP_201_CREATED)
async def remove_user_permission(user_id: int, permission_id: int, api_key: APIKey = Depends(api_key_auth)) -> bool:
    """
    Sets a permission associated with a user.

    - Args:
        - **user_id** (int): The ID of the user for whom the permission is to be removed for.
        - **permissionID** (int): The ID of the permission to be removed.

    - Returns:
        - **bool**: True if the permission has been removed, or False if it is already not set..

    - Raise:
        - **HTTPException**: If the API key is invalid (403) or the user does not exist (404).
    """
    user = user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # find permissions to see if permission has been set already
    permissions = user_service.get_permissions(user_id)
    permission_ids = [permission.id for permission in permissions]
    if permission_id not in permission_ids:
        return False
    # delete permission
    result: bool = user_service.delete_permission(user_id, permission_id)
    return result

