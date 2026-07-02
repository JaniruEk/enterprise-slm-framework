from dynamic_graph_rag import DynamicSchemaEngine

print("Initializing Dynamic RAG Engine...")
# Point it to the new Chinook database and create a new ChromaDB collection
engine = DynamicSchemaEngine(
    db_file_path="../data/chinook.db", 
    chroma_path="../data/chroma_db_chinook" # New vector folder
)
print("Engine ready! Type 'exit' to quit.\n")

while True:
    print("-" * 60)
    user_query = input("Enter a test query: ")
    
    if user_query.lower() in ['exit', 'quit']:
        print("Shutting down tester...")
        break
        
    print(f"\n[Searching for Context...]")
    context = engine.retrieve_optimized_context(user_query)
    
    print("\n=== EXTRACTED SCHEMA CONTEXT ===")
    print(context)
    print("================================\n")