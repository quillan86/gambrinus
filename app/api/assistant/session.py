from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from ...db.sqldb.services import session_service, response_service, user_service
from ...services.security import api_key_auth
from fastapi.security.api_key import APIKey
from ...services.qa.summary import SummaryService
from .models import FullResponse, Session, SessionSummary
from langchain.schema import BaseMessage
from ...services.qa.followup import FollowupService
from ...db.cachedb import cache
import pickle

router = APIRouter(
    prefix="/session",
    tags=["assistant"]
)

@router.get("/{session_id}/", response_model=Session, status_code=status.HTTP_200_OK)
async def get_session(session_id: str,
                      api_key: APIKey = Depends(api_key_auth)):
    """
    Retrieves the session of the user based on the given Session ID.

    - Args:
        - **session_id** (str): The Session ID to query.

    - Returns:
        - **dict**: The queried parts of the SQL response table relative to session ID.

    - Raise:
        - **HTTPException 403**: If the API key is invalid or the session ID is not found.
    """
    # dummy for now
    session = session_service.get_by_id(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    result = session_service.row2dict(session)
    return result


@router.get("/{session_id}/responses/", response_model=list[FullResponse], status_code=status.HTTP_200_OK)
async def get_session_responses(session_id: str,
                      api_key: APIKey = Depends(api_key_auth)):
    """
    Retrieves the responses of the user based on the given Session ID.

    - Args:
        - **session_id** (str): The Session ID to query.

    - Returns:
        - **list[dict]**: The queried parts of the SQL response table relative to session ID.

    - Raise:
        - **HTTPException 403**: If the API key is invalid or the session ID is not found.
    """
    # dummy for now
    session = session_service.get_by_id(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    responses = response_service.get_by_session(session_id)
    return responses

@router.put("/{session_id}/")
async def modify_session(session_id: int, name: str,
                         api_key: APIKey = Depends(api_key_auth)) -> str:
    """
    Modifies the session.

    - Args:
        - **session_id** (str): The Session ID to query.

    - Returns:
        - **list[dict]**: The queried parts of the SQL response table relative to session ID.

    - Raise:
        - **HTTPException 403**: If the API key is invalid or the session ID is not found.
    :return:
    """
    session = session_service.get_by_id(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if name == session.name:
        # same
        return name
    else:
        session_id = session.id

        obj = {}
        obj['id'] = session_id
        obj['name'] = name
        # update response
        session_service.update(obj)
    return name


@router.delete("/{session_id}/", status_code=status.HTTP_200_OK)
async def delete_session(session_id: int, api_key: APIKey = Depends(api_key_auth)) -> bool:
    """
    Deletes a specific session from the database using the provided session ID.


    - Args:
        - **response_id** (int): The ID of the session to be retrieved.

    - Returns:
        - **bool**: Whether the session has been deleted or not.

    - Raises:
        - **HTTPException**: If the API key is invalid (403) or if the session ID does not exist in the database (404).
    """
    session: Optional[str] = session_service.get_by_id(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session ID not found.")
    result: bool = session_service.delete([session_id])
    return result


@router.post("/user/{user_id}/", status_code=status.HTTP_201_CREATED)
async def create_session(user_id: int, name: str, api_key: APIKey = Depends(api_key_auth)) -> int:
    """
    Creates a new session for a given user.

    - Args:
        - **user_id** (int): The ID of the user for whom the session is to be created.
        - **name** (str): The name of the session.

    - Returns:
        - **int**: ID of the session created.

    - Raise:
        - **HTTPException**: If the API key is invalid (403), the user does not exist (404), or if the session could not be created for any reason (500).
    """
    user = user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # create session
    result = user_service.create_session(user_id, name)
    return result


@router.get("/user/{user_id}/", status_code=status.HTTP_200_OK)
async def get_sessions(user_id: int, api_key: APIKey = Depends(api_key_auth)):
    """
    Gets the history of all sessions of a user.
    :param user_id:
    :param api_key:
    :return:
    """
    user = user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    sessions = session_service.get_by_user_id(user_id)
    return sessions

@router.get("/{session_id}/followup/", status_code=status.HTTP_200_OK)
async def followup_recommendations(session_id: int,
                                   redis_client: cache = Depends(cache),
                                   api_key: APIKey = Depends(api_key_auth)) -> list[str]:
    """
    Recommend follow-up prompts the user can suggest next after the last response.

    - Args:
        - **session_id** (int): The ID of the session in the database. The session is attached to a user.

    - Returns:
        - **list**: A list of three prompts that the user might ask next.

    - Raises:
        - **HTTPException**: If the API key is invalid (403), the session does not exist(404), or if the AI fails to generate an answer (500).
    :return:
    """
    # 1) authorize user and session
    session = session_service.get_by_id(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session does not exist")
    chat_history: list[BaseMessage] = session_service.get_session_history(session_id)
    chat_history_short = tuple([chat.content for chat in chat_history[-6:]])
    # hash chat nistory for cache
    if len(chat_history_short) > 0:
        chat_history_hash = hash(chat_history_short)
    if chat_history is None:
        return []
    if len(chat_history) == 0:
        return []
    # find if cached

    if len(chat_history_short) > 0:
        if (cached_followup := redis_client.get(f"followup_{chat_history_hash}")) is not None:
            return pickle.loads(cached_followup)
    result = await FollowupService.run(chat_history)
    # cache result
    if len(chat_history_short) > 0:
        redis_client.set(f"followup_{chat_history_hash}", pickle.dumps(result))
    return result


@router.get("/{session_id}/summary/", response_model=SessionSummary, status_code=status.HTTP_200_OK)
async def session_summary(session_id: int, api_key: APIKey = Depends(api_key_auth)) -> dict[str, str]:
    """
    Summarizes a session's conversation.

    - Args:
        - **response_id** (int): The ID of the session to be retrieved.

    - Returns:
        - **dict[str]**: Summary of the session.

    - Raises:
        - **HTTPException**: If the API key is invalid (403) or if the session ID does not exist in the database (404).
    """

    chat_history: list[BaseMessage] = session_service.get_session_history(session_id)

    result: str = await SummaryService.run(chat_history)

    return {"summary": result}