from neo4j import GraphDatabase
from app.core.config import settings

# Lazy initialization - don't connect at import time
_driver = None


def _get_driver():
    """Lazy load the Neo4j driver."""
    global _driver
    if _driver is None:
        print(f"\n🔌 Connecting to Neo4j at {settings.NEO4J_URI}...")
        _driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        )
        try:
            _driver.verify_connectivity()
            print("✅ Connected to Neo4j Graph Database")
        except Exception as e:
            print(f"⚠️ Warning: Could not verify Neo4j connection: {e}")
    return _driver


def add_relationship(head: str, relation_type: str, tail: str):
    """
    Creates a fact in the graph: (Head)-[RELATION]->(Tail)
    Example: (Elon Musk)-[OWNS]->(SpaceX)
    """
    try:
        driver = _get_driver()
        query = """
        MERGE (h:Entity {name: $head_name})
        MERGE (t:Entity {name: $tail_name})
        MERGE (h)-[r:RELATION {type: $rel_type}]->(t)
        RETURN h, r, t
        """

        print(f"\n📊 GRAPH UPDATE")
        print(f"   ({head}) -[{relation_type}]-> ({tail})")

        with driver.session() as session:
            session.run(query, head_name=head, tail_name=tail, rel_type=relation_type)
            print(f"   ✅ Relationship saved to Neo4j")
    except Exception as e:
        print(f"   ⚠️ Failed to add relationship: {e}")


def get_entity_facts(entity_name: str):
    """
    Finds everything connected to a specific entity.
    Uses case-insensitive partial matching.
    """
    try:
        driver = _get_driver()
        # Case-insensitive matching using toLower() and CONTAINS
        query = """
        MATCH (e:Entity)-[r]->(target)
        WHERE toLower(e.name) CONTAINS toLower($name)
        RETURN e.name as entity, r.type as relation, target.name as target
        """
        
        print(f"\n🔍 GRAPH LOOKUP")
        print(f"   Searching for: '{entity_name}' (case-insensitive)")
        
        results = []
        with driver.session() as session:
            result = session.run(query, name=entity_name)
            for record in result:
                fact = f"{record['entity']} {record['relation']} {record['target']}"
                results.append(fact)
        
        if results:
            print(f"   ✅ Found {len(results)} facts:")
            for fact in results:
                print(f"   • {fact}")
        else:
            print(f"   No facts found containing '{entity_name}'")
        
        return results
    except Exception as e:
        print(f"   ⚠️ Failed to get entity facts: {e}")
        return []


def close_driver():
    global _driver
    if _driver:
        _driver.close()
        _driver = None
        print("🔌 Neo4j connection closed")