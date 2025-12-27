"""Check Neo4j connectivity using NEO4J_URI / NEO4J_USERNAME / NEO4J_PASSWORD / NEO4J_DATABASE

Usage:
  python scripts/check_neo4j.py
"""
from dotenv import load_dotenv
import os
import sys
from neo4j import GraphDatabase, basic_auth

load_dotenv()


def check(timeout=5):
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    pwd = os.getenv("NEO4J_PASSWORD")
    db = os.getenv("NEO4J_DATABASE")
    if not uri or not user or not pwd:
        print("NEO4J_URI/NEO4J_USERNAME/NEO4J_PASSWORD must be set")
        return False
    try:
        driver = GraphDatabase.driver(uri, auth=basic_auth(user, pwd))
        with driver.session(database=db) as s:
            r = s.run("RETURN 1 AS v")
            val = r.single()["v"]
        print("Neo4j OK:", val)
        driver.close()
        return True
    except Exception as e:
        print("Neo4j ERROR:", e)
        return False

if __name__ == '__main__':
    ok = check()
    sys.exit(0 if ok else 1)
