import sqlite3
import requests
from dynamic_graph_rag import DynamicSchemaEngine

print("==================================================")
print("   ENTERPRISE MULTI-AGENT DATABASE SELECTOR")
print("==================================================")
print("1. Enterprise HR Database (Custom Pillar 1 Data)")
print("2. Chinook Music Store (Real-World Benchmark)")
print("==================================================")

choice = input("Select the workspace you want to load (1 or 2): ").strip()

if choice == '2':
    target_db = "../data/chinook.db"
    target_chroma = "../data/chroma_db_chinook"
    print("\n[System] Booting Chinook Music Store environment...")
else:
    target_db = "../data/enterprise.db"
    target_chroma = "../data/chroma_db"
    print("\n[System] Booting Enterprise HR environment...")

# 1. Initialize engine pointed to the selected workspace
engine = DynamicSchemaEngine(
    db_file_path=target_db, 
    chroma_path=target_chroma 
)
print("[System] Framework fully online! Type 'exit' to stop.\n")

while True:
    print("-" * 60)
    user_query = input("Ask a question about the database: ")
    
    if user_query.lower() in ['exit', 'quit']:
        print("Shutting down end-to-end environment...")
        break
        
    if not user_query.strip():
        continue

    # Step A: Harvest the schemas dynamically
    print("\n[Step 1/4] Retrieving schema context via dynamic graph extraction...")
    schema_context = engine.retrieve_optimized_context(user_query)

    # Step B: Build prompt
    prompt = f"""You are an expert SQL generator. Write a valid SQLite query to answer the request.
Output ONLY the raw SQL query string. Do not use markdown blocks, backticks, or text explanations.
CRITICAL RULE: Do NOT use table aliases (e.g. use employees.first_name instead of e.first_name). Use explicit JOINs.

Schema Context:
{schema_context}

Request: {user_query}
SQL Query:"""

    print("\n[Agent 2] Forwarding context to local Phi-3 server...")
    
    max_retries = 3
    current_prompt = prompt
    success = False

    for attempt in range(max_retries):
        try:
            # Ask the AI to write the query
            response = requests.post("http://localhost:11434/api/generate", json={
                "model": "phi3",
                "prompt": current_prompt,
                "stream": False
            }, timeout=30)
            
            raw_sql = response.json().get('response', '').strip()
            
            # THE FIX: This is now safely on one line
            cleaned_sql = raw_sql.replace("```sql", "").replace("```", "").strip()
            
            if cleaned_sql.endswith(';'):
                cleaned_sql = cleaned_sql[:-1]

            print("\n" + "="*60)
            print(f"[Attempt {attempt + 1}/{max_retries}] AI GENERATED SQL:")
            print(cleaned_sql)
            print("="*60)

            # Agent 3 (Validator) attempts to run the query
            print(" -> [Agent 3] Validating syntax against database...")
            conn = sqlite3.connect(target_db) # Dynamically connects to the chosen DB!
            cursor = conn.cursor()
            
            cursor.execute(cleaned_sql)
            records = cursor.fetchall()
            
            print("\n" + "="*60)
            print("FINAL RETRIEVED DATA ROWS:")
            print("="*60)
            if records:
                for row in records:
                    print(f" -> {row[0] if len(row) == 1 else row}")
            else:
                print(" -> [Empty Result Set] Query valid, but 0 matching records found.")
            print("="*60 + "\n")
            
            conn.close()
            success = True
            break # Exit the loop, query succeeded!

        except sqlite3.OperationalError as db_error:
            # AGENT 3 CATCHES ERROR
            print(f" -> [Agent 3 Triggered]: Database rejected query. Error: {db_error}")
            if attempt < max_retries - 1:
                print(" -> Feedback loop initiated. Forcing LLM to rewrite...")
                current_prompt += f"\n\nYour previous SQL query:\n{cleaned_sql}\n\nFailed with this database error: {db_error}\nRewrite the query to fix this error. Output ONLY the raw SQL."
            conn.close()
            
        except requests.exceptions.ConnectionError:
            print("\n[System Error]: Local server unreachable. Ensure Ollama is running.")
            break
        except Exception as e:
            print(f"\n[Critical Failure]: {e}")
            break

    if not success:
        print("\n[Pipeline Aborted] The AI failed to write a valid query after 3 attempts.")