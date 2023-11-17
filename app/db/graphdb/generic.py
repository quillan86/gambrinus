from neo4j import Driver
from . import graph_driver


class GraphService:
    driver: Driver = graph_driver
