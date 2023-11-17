from fastapi.security.api_key import APIKeyCookie, APIKeyHeader

API_KEY_NAME: str = "access_token"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)
