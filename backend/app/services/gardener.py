import json
import time
import re
from qdrant_client.http import models
from app.services import graph_service
from app.services.llm import llm_service
from app.services.memory_service import client as qdrant_client, COLLECTION_NAME

async def prune_graph():
    """
    Scans the graph for similar entities and merges them.
    Example: Merges 'Space X' into 'SpaceX'.
    """
    print("Gardener: Starting graph maintenance...")

    # 1. Fetch all entity names from Neo4j
    query = "MATCH (n:Entity) RETURN n.name as name"
    entities = []
    
    try:
        with graph_service.driver.session() as session:
            result = session.run(query)
            entities = [record["name"] for record in result]
            
    except Exception as e:
        print(f"Gardener Error: Could not fetch entities from Graph. {e}")
        return

    if len(entities) < 2:
        print("Gardener: Not enough data to prune.")
        return

    print(f"Gardener: Analyzing {len(entities)} entities for duplicates...")

    # 2. Ask AI to find duplicates in this list
    prompt = f"""
    Analyze this list of entities: {entities}
    Identify pairs that refer to the SAME real-world object but have slightly different spellings or capitalizations.
    
    Return ONLY a valid JSON list of objects. Format:
    [
      {{"keep": "SpaceX", "merge": "Space X"}},
      {{"keep": "Elon Musk", "merge": "elon musk"}}
    ]
    
    If no duplicates are found, return empty list [].
    Do not add any explanations or markdown. Just the JSON.
    """

    response_text = await llm_service.generate_answer(prompt, context="System Maintenance Mode")
    
    # 3. Clean and Parse JSON (Robust Logic)
    try:
        cleaned_text = re.sub(r"```json|```", "", response_text).strip()
        merge_pairs = json.loads(cleaned_text)
        
    except json.JSONDecodeError:
        print(f"Gardener Error: AI returned invalid JSON.\nRaw: {response_text}")
        return

    if not merge_pairs:
        print("Gardener: No duplicates found.")
        return

    print(f"Gardener: Found {len(merge_pairs)} duplicates to merge.")

    # 4. Execute Merges in Neo4j
    merge_query = """
    MATCH (keep:Entity {name: $keep_name})
    MATCH (discard:Entity {name: $discard_name})
    CALL apoc.refactor.mergeNodes([keep, discard], {properties: 'discard', mergeRels: true})
    YIELD node
    RETURN node.name
    """

    with graph_service.driver.session() as session:
        for pair in merge_pairs:
            keep = pair.get('keep')
            discard = pair.get('merge')
            
            print(f"Merging '{discard}' -> '{keep}'...")
            
            try:
                session.run(merge_query, keep_name=keep, discard_name=discard)
                
            except Exception as e:
                print(f"APOC merge failed (Plugin missing ?).")

    print("Gardener: Graph pruning complete.")

def clean_old_vectors(days_old: int = 365):
    """
    Deletes Qdrant vectors older than 365 days to save space.
    """
    print(f"Gardener: Cleaning vectors older than {days_old} days...")
    
    cutoff_timestamp = time.time() - (days_old * 24 * 60 * 60)
    
    try:
        # Define the filter: "timestamp < cutoff"
        time_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="timestamp",
                    range=models.Range(
                        lt=cutoff_timestamp
                    )
                )
            ]
        )
        
        # Execute deletion
        result = qdrant_client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=models.FilterSelector(
                filter=time_filter
            )
        )
        print(f"Gardener: Old memories deleted. Status: {result}")
        
    except Exception as e:
        print(f"Gardener Error: Failed to clean Qdrant. {e}")