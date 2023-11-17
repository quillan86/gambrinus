from gptcache import cache
import os
from gptcache.manager import get_data_manager, CacheBase, VectorBase
from .embeddings import onnx

sql_database = {
    'hostname': os.getenv("GAMBRINUS_SQL_CACHE_HOST"),
    'port': os.getenv("GAMBRINUS_SQL_CACHE_PORT"),
    'user': os.getenv("GAMBRINUS_SQL_CACHE_USER"),
    'password': os.getenv("GAMBRINUS_SQL_CACHE_PASSWORD"),
    'database': os.getenv("GAMBRINUS_SQL_CACHE_DATABASE")
}

vector_database = {
    'host': os.getenv('GAMBRINUS_MILVUS_HOST'),
    'port': os.getenv('GAMBRINUS_MILVUS_PORT'),
    'user': os.getenv('GAMBRINUS_MILVUS_USER'),
    'password': os.getenv('GAMBRINUS_MILVUS_PASSWORD'),
    'secure': True,
    'collection_name': os.getenv('GAMBRINUS_MILVUS_CACHE_COLLECTION'),
    'search_params': None,
    'local_mode': False,
}

SQL_URL = f"mssql+pyodbc://{sql_database['user']}:{sql_database['password']}@{sql_database['hostname']}:{sql_database['port']}/{sql_database['database']}?driver=ODBC+Driver+18+for+SQL+Server"

cache_base = CacheBase('sqlserver', sql_url=SQL_URL, table_name="gptcache")
vector_base = VectorBase('milvus', host=vector_database['host'], port=vector_database['port'],
                         user=vector_database['user'], password=vector_database['password'], secure=vector_database['secure'],
                         collection_name=vector_database['collection_name'], search_params=vector_database['search_params'], local_mode=vector_database['local_mode'],
                         dimension=onnx.dimension)

data_manager = get_data_manager(cache_base, vector_base, max_size=5000, clean_size=200)
