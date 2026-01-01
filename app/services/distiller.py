from app.services.llm import llm_service
from app.services import graph_service

def distill_conversion(user_query: str, ai_response: str):
    """
    Analyzes the Q&A pair to find new facts and saves them to the Graph.
    This should run in the background.
    """    
    
    print("Distiller started: extracting knowledge...")
    
    full_text = f"Question: {user_query}\nAnswer:{ai_response}"
    facts = llm_service.extract_facts(full_text)
    
    if not facts:
        print("No facts found to distill.")
        return
    
    print(f"Found {len(facts)} new facts. Saving to Graph...")
    
    for fact in facts:
        head = fact["head"]
        tail = fact["tail"]
        relation = fact["relation"]
        
        if head and relation and tail:
            relation = relation.upper().replace(" ", "_").strip()
            
            graph_service.add_relationship(head, relation, tail)
            
    print("Distillation complete.")