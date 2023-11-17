from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security.api_key import APIKey
from typing import Optional
from ...db.cachedb import cache
from ...db.sqldb.services import session_service, response_service
from ...services.qa.agents import OpenAIFunctionAgentService
from ...services.security import api_key_auth
from .models import Feedback, ResponseAndFeedback, Response
from langchain.schema import BaseMessage
from openai.error import InvalidRequestError
import traceback
import time
import datetime
import pickle

router = APIRouter(
    prefix="/response",
    tags=["assistant"]
)


async def get_answer(user_id: int, session_id: int, question: str, redis_client, max_iterations: int = 2) -> tuple[str, str, str, list[dict]]:
    """
    Generates an answer and intent for a given question using a session ID for context.
    This is an alternate methodology than the other methodology.

    This function utilizes a tool + agent based system to generate answers
    to produce an answer and an intent for a given question. Less services needed.
    Do not put into production until Azure OpenAI functions functionality is in place:
    we want to use that for the agent.

    - Args:
        - **user_id** (int): The ID of the user for context of the generation of the system message.
        - **session_id** (int): The ID of the session for context in the generation of the answer.
        - **question** (str): The question for which an answer is to be generated.

    - Returns:
        - **tuple[str, str]**: A tuple containing the generated answer and its associated intent.

    - Raises:
        - **Exception**: If the topic classifier, intent classifier, or answer generation service fails.
    """
    # get session history
    chat_start = time.time()
    chat_history: list[BaseMessage] = session_service.get_session_history(session_id)
    # short chat history for hashing
    chat_history_short = tuple([chat.content for chat in chat_history[-6:]])
    # used for followups
    chat_history_hash = hash(chat_history_short)
    # used for responses - there can be unique user information
    user_chat_history_hash = hash((user_id,) + chat_history_short + (question,))
    chat_end = time.time()
    chat_time = chat_end - chat_start
    print(f"Chat History Time: {chat_time}")
    # delete followup cache
    if len(chat_history_short) > 0:
        redis_client.delete(f"followup_{chat_history_hash}")

    if (cached_response := redis_client.get(f"response_{user_chat_history_hash}")) is not None:
        answer, sources, intent, tools = pickle.loads(cached_response)
        return answer, sources, intent, tools

    agent = OpenAIFunctionAgentService(chat_history=chat_history, max_iterations=max_iterations, user_id=user_id)
    agent_output = agent.run(question)
    answer = agent_output['response']
    sources = agent_output['sources']
    intent = agent_output['intent']
    tools = agent_output['tools']
    agent_end = time.time()
    agent_time = agent_end - chat_end
    print(f"Agent Time: {agent_time}")

    # cache response
    redis_client.set(f"response_{user_chat_history_hash}", pickle.dumps([answer, sources, intent, tools]))

    return answer, sources, intent, tools


@router.get("/{response_id}/", response_model=ResponseAndFeedback, status_code=status.HTTP_200_OK)
async def get_response(response_id: int, api_key: APIKey = Depends(api_key_auth)):
    """
    Retrieves a specific response from the database using the provided response ID.

    This function looks up the response associated with the given response ID. If a match is found,
    it returns a dictionary containing various details about the response, such as session ID, question,
    answer, intent, and feedback information.

    - Args:
        - **response_id** (int): The ID of the response to be retrieved.

    - Returns:
        - **dict**: A dictionary containing details about the response, including the session ID, the question asked,
        the answer generated by the AI, the intent of the question, and feedback information.

    - Raises:
        - **HTTPException**: If the API key is invalid (403) or if the response ID does not exist in the database (404).
    """
    # look up question
    response: Optional[str] = response_service.get_by_id(response_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Response ID not found.")
    else:
        return {"session_id": response.session_id,
                "human_created_at": response.human_created_at,
                "human_updated_at": response.human_updated_at,
                "assistant_created_at": response.assistant_created_at,
                "assistant_updated_at": response.assistant_updated_at,
                "question": response.question,
                "answer": response.answer,
                "intent": response.intent,
                "sources": response.sources,
                "feedback_check": response.feedback_check,
                "feedback_category": response.feedback_category,
                "feedback_comment": response.feedback_comment
                }


@router.post("/", response_model=Response, status_code=status.HTTP_201_CREATED)
async def answer_question(session_id: int, question: str, max_iterations: int = 2,
                          redis_client: cache = Depends(cache), api_key: APIKey = Depends(api_key_auth)) -> dict[str, Optional[str]]:
    """
    Given a session, this API call sends a question to the AI and returns the generated answer.
    This is the primary interface for interacting with the AI. The question is sent to the AI, which generates an answer.
    Both the question and the answer are stored in the SQL database.
    The generated answer is returned and intended to be displayed by a chatbot.

    - Args:
        - **session_id** (int): The ID of the session in the database. The session is attached to a user.
        - **question** (str): The question that is to be asked to the AI.
        - **max_iterations** (int): The maximum number of iterations of tools to call for the prompt. Higher numbers means richer answers, but have lower latency.

    - Returns:
        - **dict**: A dictionary containing the session ID, the question asked, and the answer generated by the AI.

    - Raises:
        - **HTTPException**: If the API key is invalid (403), the session does not exist(404), or if the AI fails to generate an answer (500).
    """

    human_created_at = datetime.datetime.now(datetime.timezone.utc)
    # 1) authorize user and session
    session = session_service.get_by_id(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session does not exist")
    try:
        print(f"Question: {question}")
        if question.lower().strip() == "help":
            answer = """Relax, grab a beer, I'll take care of everything!

            The following are some of my capabilities:

            1. Brewing Knowledge: Inquiries and questions for basic information on ingredients, the brewing process, or beer in general, from the perspective of someone crafting beer.
            2. Flavor Profiling: Identifying and adjusting the ingredients for the taste and aroma of beer.
            3. Recipe Finding: Easily find the perfect beer recipe, learn about its unique properties, or explore representative recipes for specific beer styles.
            
            All of these capabilities should generate citations - if you are not getting citations, try saying using the capability, such as "Use Brewing Knowledge" at the end of a question.
            
            Explore what I can do by asking some of these questions:

            - Cost Savings: "What malt can I use as a cost-effective substitute in my Pale Ale recipe?"
            - Recipe Experimentation: "How will swapping Cascade hops for Amarillo affect my IPA?"
            - Allergen Concerns: "Which gluten-free grains can replace barley in a stout?"
            - Equipment Guidance: "What's the best fermenter for a beginner brewer?"
            - Flavor Profiling: "How will adding Chocolate Malt change the taste of my porter?"
            - Efficient Brewing: "What's the optimal fermentation time for a Belgian Tripel?"
            - Seasonal Brews: "What ingredients will create a refreshing summer ale?"
            - Scaling Production: "How can I double my current batch size without losing quality?"
            """
            sources: Optional[str] = None
            intent: str = "help"
        else:
            user_id = session.user_id
            answer, sources, intent, _ = await get_answer(user_id, session_id, question, redis_client, max_iterations=max_iterations)
    except InvalidRequestError as e:
        print(traceback.print_exc())
        intent: str = e.code
        if e.code == 'prompt_filter':
            answer: str = "The response was filtered due to the prompt triggering Estimand's content management policy. Please modify your prompt and retry."
        else:
            answer: str = "Oops! I am getting a lot of messages right now. Please try again later."
        sources: Optional[str] = None
    except Exception as e:
        print(traceback.print_exc())
        answer: str = "Oops! I am getting a lot of messages right now. Please try again later."
        intent: str = "error"
        sources: Optional[str] = None
    # store prompt in user database
    response = session_service.create_response(session_id, human_created_at, question, answer, intent, sources)
    # return answer
    return {"id": response.id, "human_created_at": response.human_created_at,
            "assistant_created_at": response.assistant_created_at,
            "answer": answer, "sources": sources, "intent": intent}


@router.put("/", response_model=Response, status_code=status.HTTP_200_OK)
async def modify_question(response_id: int, question: str, redis_client: cache = Depends(cache), max_iterations: int = 2, api_key: APIKey = Depends(api_key_auth)) -> dict[str, Optional[str]]:
    """
    Modifies an existing question to the AI in the database.

    This function allows for modifying the question asked to the AI, linked by the response ID.
    The modified question is then processed by the AI to produce a new answer. Both the new question and answer
    are updated in the database.
    If the question is the same, the AI is not called and the database is not modified.

    - Args:
        - **response_id** (int): The ID of the response in the database.
        - **question** (str): The new question that is to be asked to the AI.

    - Returns:
        - **dict**: A dictionary containing the session ID, the modified question, and the newly generated answer by the AI.

    - Raises:
        - **HTTPException**: If the API key is invalid (403), the response ID does not exist (404), or if the AI fails to generate an answer (500).
    """
    # look up question
    human_updated_at = datetime.datetime.now(datetime.timezone.utc)
    response = response_service.get_by_id(response_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Response ID not found.")
    elif response.question == question:
        # same
        return response.answer
    else:
        session_id = response.session_id
        user_id = session_service.get_by_id(session_id).user_id
        try:
            print(f"Question: {question}")
            answer, sources, intent, _ = await get_answer(user_id, session_id, question, redis_client, max_iterations=max_iterations)
            # store prompt in user database
        except Exception as e:
            print(traceback.print_exc())
            answer: str = "Oops! I am getting a lot of messages right now. Please try again later."
            intent: str = "error"
            sources: Optional[str] = None
        assistant_updated_at = datetime.datetime.now(datetime.timezone.utc)

        obj = {}
        obj['id'] = response.id
        obj['human_updated_at'] = human_updated_at
        obj['assistant_updated_at'] = assistant_updated_at
        obj['question'] = question
        obj['answer'] = answer
        obj['intent'] = intent
        obj['sources'] = sources
        # reset feedback
        obj['feedback_check'] = None
        obj['feedback_category'] = None
        obj['feedback_comment'] = None
        # update response
        response_service.update(obj)
        return {"answer": answer, "sources": sources, "intent": intent}


@router.delete("/{response_id}/", status_code=status.HTTP_200_OK)
async def delete_response(response_id: int, redis_client: cache = Depends(cache), api_key: APIKey = Depends(api_key_auth)):
    """
    Deletes a specific response from the database using the provided response ID.


    - Args:
        - **response_id** (int): The ID of the response to be retrieved.

    - Returns:
        - **bool**: Whether the response has been deleted or not.

    - Raises:
        - **HTTPException**: If the API key is invalid (403) or if the response ID does not exist in the database (404).
    """
    response = response_service.get_by_id(response_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Response ID not found.")
    session = session_service.get_by_id(response.session_id)
    chat_history: list[BaseMessage] = session_service.get_session_history(session.id)
    chat_history_short = chat_history[-6:]
    user_id = session.user_id
    # used for responses - there can be unique user information
    user_chat_history_hash = hash((user_id,) + chat_history_short)
    # delete response cache
    redis_client.delete(f"response_{user_chat_history_hash}")
    result: bool = response_service.delete([response_id])
    return result


@router.put("/feedback/", response_model=Feedback, status_code=status.HTTP_200_OK)
async def add_feedback(response_id: int, check: bool, category: Optional[str] = None, comment: Optional[str] = None, api_key: APIKey = Depends(api_key_auth)):
    """
    Adds or updates feedback for a specific response.

    This function allows the user to provide feedback for a given response. Feedback includes an optional check
    (representing approval or rejection of the answer), a category, and a comment. This feedback is then associated
    with the response in the database.

    - Args:
        - **response_id** (int): The ID of the response to which feedback is to be added or updated.
        - **check** (Optional[bool]): A boolean value representing the approval (True), rejection (False),
                                or neutrality (None) of the feedback.
        - **category** (Optional[str]): The category of the feedback, or None if there is no category when check is True or None.
        - **comment** (Optional[str]): A comment associated with the feedback, or None is there is no comment when check is True or None.

    - Returns:
        - **dict**: A dictionary containing the session ID and the added or updated feedback.

    - Raises:
        - **HTTPException**: If the API key is invalid (403) or if the response ID does not exist in the database (404).
    """
    response = response_service.get_by_id(response_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Response ID not found.")
    else:
        if check is True:
            feedback_check = True
        elif check is False:
            feedback_check = False
        else:
            feedback_check = None

        session_id = response.session_id
        obj = {}
        obj['id'] = response.id
        obj['feedback_check'] = feedback_check
        obj['feedback_category'] = category
        obj['feedback_comment'] = comment

        response_service.update(obj)

        return {"session_id": session_id, "question": response.question,
                "answer": response.answer,
                "intent": response.intent,
                "feedback_check": feedback_check,
                "feedback_category": category, "feedback_comment": comment}
