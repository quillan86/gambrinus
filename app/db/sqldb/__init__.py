import pyodbc
from sqlalchemy import create_engine
import urllib
import os
from dotenv import load_dotenv

if os.getenv("GAMBRINUS_ENV") is None:
    load_dotenv()

databases: dict[str, dict[str, str]] = {
    'dev': {
            'hostname': os.getenv("GAMBRINUS_SQL_DEV_HOST"),
            'port': os.getenv("GAMBRINUS_SQL_DEV_PORT"),
            'user': os.getenv("GAMBRINUS_SQL_DEV_USER"),
            'password': os.getenv("GAMBRINUS_SQL_DEV_PASSWORD"),
            'database': os.getenv("GAMBRINUS_SQL_DEV_DATABASE")
    },
    'staging': {
        'hostname': os.getenv("GAMBRINUS_SQL_STAGING_HOST"),
        'port': os.getenv("GAMBRINUS_SQL_STAGING_PORT"),
        'user': os.getenv("GAMBRINUS_SQL_STAGING_USER"),
        'password': os.getenv("GAMBRINUS_SQL_STAGING_PASSWORD"),
        'database': os.getenv("GAMBRINUS_SQL_STAGING_DATABASE")
    },
    'prod': {
        'hostname': os.getenv("GAMBRINUS_SQL_PROD_HOST"),
        'port': os.getenv("GAMBRINUS_SQL_PROD_PORT"),
        'user': os.getenv("GAMBRINUS_SQL_PROD_USER"),
        'password': os.getenv("GAMBRINUS_SQL_PROD_PASSWORD"),
        'database': os.getenv("GAMBRINUS_SQL_PROD_DATABASE")
    }
}

env = os.getenv("GAMBRINUS_ENV")

# env = 'prod'

database: dict[str, str] = databases[env]

# print(database)

driver: str = "{ODBC Driver 18 for SQL Server}"

# https://stackoverflow.com/questions/53704187/connecting-to-an-azure-database-using-sqlalchemy-in-python

sqlstring = rf"Driver={driver};Server=tcp:{database['hostname']},{database['port']};Database={database['database']};Uid={database['user']};Pwd={database['password']};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

params = urllib.parse.quote_plus(sqlstring) # urllib.parse.quote_plus for python 3
conn_str = f'mssql+pyodbc:///?odbc_connect={params}'
engine = create_engine(conn_str,
                       pool_size=25, max_overflow=50, pool_timeout=60,
                       pool_recycle=3600,
                       echo=True)
