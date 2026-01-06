from app.services.llm import llm_service
from app.services import graph_service

async def distill_conversation(user_query: str, ai_response: str):
    """
    Analyzes the Q&A pair to find new facts and saves them to the Graph.
    This should run in the background.
    """    
    try:
        print(f"\n🧪 DISTILLER")
        print(f"   Analyzing conversation for facts...")
        print(f"   Q: '{user_query[:60]}...'")
        print(f"   A: '{ai_response[:60]}...'")
        
        full_text = f"Question: {user_query}\nAnswer:{ai_response}"
        facts = await llm_service.extract_facts(full_text)
        
        if not facts:
            print("   ❌ No facts extracted")
            return
        
        print(f"   ✅ Extracted {len(facts)} facts:")
        for i, fact in enumerate(facts):
            print(f"   [{i+1}] {fact}")
        
        for fact in facts:
            # Use .get() for safe access - LLM may return different key names
            head = fact.get("head") or fact.get("subject") or fact.get("entity1")
            tail = fact.get("tail") or fact.get("object") or fact.get("entity2")
            relation = fact.get("relation") or fact.get("predicate") or fact.get("relationship") or fact.get("type")
            
            if head and relation and tail:
                relation = relation.upper().replace(" ", "_").strip()
                print(f"   → Saving: ({head}) -[{relation}]-> ({tail})")
                graph_service.add_relationship(head, relation, tail)
            else:
                print(f"   ⚠️ Skipped incomplete fact: {fact}")
                
        print("   ✅ Distillation complete")
    except Exception as e:
        print(f"   ⚠️ Distillation failed: {e}")