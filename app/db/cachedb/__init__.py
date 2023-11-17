from redis import StrictRedis
import os

databases: dict[str, dict[str, str]] = {
    'dev': {
            'hostname': os.getenv("GAMBRINUS_REDIS_DEV_HOST"),
            'port': os.getenv("GAMBRINUS_REDIS_DEV_PORT"),
            'password': os.getenv("GAMBRINUS_REDIS_DEV_PASSWORD"),
    },
    'staging': {
        'hostname': os.getenv("GAMBRINUS_REDIS_DEV_HOST"),
        'port': os.getenv("GAMBRINUS_REDIS_DEV_PORT"),
        'password': os.getenv("GAMBRINUS_REDIS_DEV_PASSWORD"),
    },
    'prod': {
        'hostname': os.getenv("GAMBRINUS_REDIS_PROD_HOST"),
        'port': os.getenv("GAMBRINUS_REDIS_PROD_PORT"),
        'password': os.getenv("GAMBRINUS_REDIS_PROD_PASSWORD"),
    }
}

env = os.getenv("GAMBRINUS_ENV")

database: dict[str, str] = databases[env]


def cache():
    return StrictRedis(host=database['hostname'], port=database['port'], db=0,
                 password=database['password'], ssl=True)

__all__ = ['cache']
