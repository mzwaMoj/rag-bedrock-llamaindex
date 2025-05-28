"""
RAG System Functionality Test
Test if the RAG system can properly answer questions about loaded documents
"""
import sys
import os
sys.path.append('.')

from core.rag_system import RAGSystem

def test_rag_functionality():
    """Test RAG system functionality with actual queries"""
    print("🧪 Testing RAG System Functionality")
    print("=" * 50)
      # Initialize RAG system
    print("🚀 Initializing RAG System...")
    rag_system = RAGSystem(data_directory="./data", aws_region="eu-central-1")
    
    # Initialize the system
    success = rag_system.initialize_system()
    if not success:
        print("❌ RAG system initialization failed")
        return False
    
    print(f"✅ RAG System initialized with {len(rag_system.documents)} documents")
    
    # Test queries
    test_queries = [
        "What is BOP reporting and what documents are required?",
        "What are the main validation rules for Balance of Payments?",
        "What is the Currency and Exchanges Manual about?",
        "What are the technical specifications for BOP reporting?"
    ]
    
    print("\n📝 Testing Sample Queries:")
    print("-" * 40)
    
    for i, query in enumerate(test_queries, 1):
        try:
            print(f"\n{i}. Query: {query}")
            print("   Searching...")
            
            result = rag_system.query_documents(query)
            
            if result.get("error"):
                print(f"   ❌ Error: {result['error']}")
            elif result.get("response"):
                answer = result["response"][:200] + "..." if len(result["response"]) > 200 else result["response"]
                print(f"   ✅ Answer: {answer}")
                
                # Check for sources
                sources = result.get("sources", [])
                if sources:
                    print(f"   📄 Sources: {len(sources)} documents referenced")
                    for j, source in enumerate(sources[:2], 1):
                        score = source.get("score", 0)
                        preview = source.get("text_preview", "")[:100] + "..."
                        print(f"      {j}. Score: {score:.3f} - {preview}")
                else:
                    print("   📄 Sources: No source information available")
            else:
                print("   ❌ No response received")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 RAG System Functionality Test Complete")
    return True

if __name__ == "__main__":
    test_rag_functionality()
