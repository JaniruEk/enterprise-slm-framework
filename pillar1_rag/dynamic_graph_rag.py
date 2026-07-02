import sqlite3
# pyrefly: ignore [missing-import]
import chromadb

class DynamicSchemaEngine:
    def __init__(self, db_file_path="../data/enterprise.db", chroma_path="../data/chroma_db"):
        self.db_path = db_file_path
        
        # 1. Connect to Vector DB and get or create the collection automatically
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.client.get_or_create_collection(name="robust_schema")
        
        # 2. Automatically map the database structural relationships
        self.dependency_graph = self._reflect_database_schema()
        
        # 3. Automatically populate ChromaDB if it's a brand new database
        self._auto_ingest_ddl_if_empty()

    def _reflect_database_schema(self):
        """DATABASE REFLECTION: Extracts foreign key maps dynamically from system catalogs."""
        graph = {}
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                graph[table] = []
                cursor.execute(f"PRAGMA foreign_key_list({table});")
                fk_records = cursor.fetchall()
                
                for record in fk_records:
                    parent_table = record[2]
                    if parent_table not in graph[table]:
                        graph[table].append(parent_table)
                        
            conn.close()
            print(f"[Initialization] Successfully reflected graph for {len(tables)} tables.")
            return graph
            
        except Exception as e:
            print(f"[Reflection Error]: Failed to read system catalog. {e}")
            return {}

    def _auto_ingest_ddl_if_empty(self):
        """SYSTEM CHECK: If ChromaDB has no records, automatically parse the live DB and inject them."""
        if self.collection.count() == 0:
            print("[ChromaDB Check] Vector index is empty. Commencing automatic schema ingestion...")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Fetch the actual CREATE TABLE statements directly from the live database
            cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            rows = cursor.fetchall()
            
            for table_name, ddl_text in rows:
                if ddl_text:
                    # Ingest the structural schema directly into your Chroma vector space
                    self.collection.add(
                        documents=[ddl_text],
                        ids=[table_name]
                    )
            conn.close()
            print(f"[ChromaDB Check] Successfully indexed {self.collection.count()} tables into vector space.")

    def get_table_ddl(self, table_name):
        """Retrieves targeted DDL layout directly from ChromaDB vector metadata."""
        result = self.collection.get(ids=[table_name])
        if result and result['documents']:
            return result['documents'][0]
        return f"-- Schema missing for: {table_name}"

    def resolve_dependencies_recursive(self, initial_table, depth=0, max_depth=2):
        """Recursively walks the dynamic database schema tree."""
        resolved_set = {initial_table}
        if depth >= max_depth:
            return resolved_set
            
        parents = self.dependency_graph.get(initial_table, [])
        for parent in parents:
            parent_dependencies = self.resolve_dependencies_recursive(parent, depth + 1, max_depth)
            resolved_set.update(parent_dependencies)
            
        return resolved_set

    def retrieve_optimized_context(self, query):
        """Hybrid search combining semantic search anchors with structural reflection loops."""
        semantic_results = self.collection.query(query_texts=[query], n_results=1)
        if not semantic_results['ids'] or not semantic_results['ids'][0]:
            return "Error: No semantic anchor discovered."
            
        primary_table = semantic_results['ids'][0][0]
        print(f"[Search Anchor] Matched: '{primary_table}'")
        
        all_required_tables = self.resolve_dependencies_recursive(primary_table, max_depth=2)
        print(f"[Graph Traversal] Identified necessary cluster: {list(all_required_tables)}")
        
        final_context_blocks = [self.get_table_ddl(t) for t in sorted(all_required_tables)]
        return "\n\n".join(final_context_blocks)