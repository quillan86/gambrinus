import os
from neo4j import GraphDatabase, Driver

databases: dict[str, dict[str, str]] = {
    'dev': {
            'hostname': os.getenv("GAMBRINUS_NEO4J_DEV_HOST"),
            'port': os.getenv("GAMBRINUS_NEO4J_DEV_PORT"),
            'user': os.getenv("GAMBRINUS_NEO4J_DEV_USER"),
            'password': os.getenv("GAMBRINUS_NEO4J_DEV_PASSWORD"),
            'database': 'neo4j'
    },
    'prod': {
        'hostname': os.getenv("GAMBRINUS_NEO4J_PROD_HOST"),
        'port': os.getenv("GAMBRINUS_NEO4J_PROD_PORT"),
        'user': os.getenv("GAMBRINUS_NEO4J_PROD_USER"),
        'password': os.getenv("GAMBRINUS_NEO4J_PROD_PASSWORD"),
        'database': 'Gambrinus'
    }
}

database: dict[str, str] = databases['dev']


# Create a new Driver instance

def create_graph_driver():
    result = GraphDatabase.driver(f"neo4j+s://{database['hostname']}:{database['port']}", auth=(database['user'], database['password']),
                                  connection_timeout=60)
    return result

graph_driver: Driver = create_graph_driver()


__all__ = ['graph_driver', 'create_graph_driver']
