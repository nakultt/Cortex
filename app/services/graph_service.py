from neo4j import GraphDatabase
from app.core.config import settings

# 1. Initialize the Neo4j Driver

driver = GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
)

def verify_connection():
    """
    Checks if we can talk to Neo4j.
    """
    try:
        driver.verify_connectivity()
        print("Connected to Neo4j Graph Database")
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")

def add_relationship(head: str, relation_type: str, tail: str):
    """
    Creates a fact in the graph: (Head)-[RELATION]->(Tail)
    Example: (Elon Musk)-[OWNS]->(SpaceX)
    """
    query = """
    MERGE (h:Entity {name: $head_name})
    MERGE (t:Entity {name: $tail_name})
    MERGE (h)-[r:RELATION {type: $rel_type}]->(t)
    RETURN h, r, t
    """

    with driver.session() as session:
        session.run(query, head_name=head, tail_name=tail, rel_type=relation_type)
        print(f"Graph Update: ({head}) -[{relation_type}]-> ({tail})")

def get_entity_facts(entity_name: str):
    """
    Finds everything connected to a specific entity.
    """
    query = """
    MATCH (e:Entity {name: $name})-[r]->(target)
    RETURN e.name, r.type, target.name
    """
    
    results = []
    with driver.session() as session:
        result = session.run(query, name=entity_name)
        for record in result:
            fact = f"{record['e.name']} {record['r.type']} {record['target.name']}"
            results.append(fact)
    
    return results

def close_driver():
    driver.close()

verify_connection()