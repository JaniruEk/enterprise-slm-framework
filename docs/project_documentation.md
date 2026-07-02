# Enterprise SLM Framework - Project Documentation

This document provides a comprehensive overview of the `enterprise-slm-framework` project, designed to help external LLMs understand the project's architecture, files, and capabilities.

## Overview

The **Enterprise SLM Framework** is a multi-agent system designed for text-to-SQL generation and database querying. It leverages Small Language Models (SLMs) running locally (via Ollama) and a Retrieval-Augmented Generation (RAG) architecture to dynamically understand relational database schemas and generate accurate SQL queries. The system incorporates a self-healing feedback loop where syntax errors in generated SQL are fed back to the LLM for correction.

## Core Capabilities

1. **Dynamic Schema Reflection**: Automatically reads SQLite databases, extracts table structures (DDL), and maps Foreign Key dependencies without hardcoded schema definitions.
2. **Structural RAG via Vector Database**: Ingests table DDLs into a ChromaDB vector space. Given a natural language query, it performs semantic search to find an "anchor" table, then recursively pulls dependent tables based on the foreign key graph.
3. **Schema Column Pruning (Context Optimization)**: Filters out database columns from the RAG schema context that are not structural keys (PK/FK) and are irrelevant to the user's query. This drastically reduces the context window and VRAM consumption.
4. **Few-Shot Context Injection**: Injects perfect SQL generation examples directly into the model's prompt to force constraints (like SQLite `LIMIT` instead of T-SQL `TOP` and non-aliased JOINs) through in-context learning.
5. **Multi-Agent Orchestration**:
   - **Agent 1 (Context Retriever)**: Uses `DynamicSchemaEngine` to retrieve optimized schema context.
   - **Agent 2 (SQL Generator)**: A local SLM (default: `phi3` via Ollama) that writes SQL queries based on the prompt and context.
   - **Agent 3 (SQL Validator)**: Executes the generated SQL against the live database.
6. **Self-Healing Feedback Loop (Smart Hinting)**: If Agent 3 encounters an `sqlite3.OperationalError`, it generates an intelligent, LLM-friendly suggestion (e.g. reminding the LLM about SQLite dialects, table hallucinations, or ambiguous columns) and loops it back into the prompt for automatic query correction (up to 3 retries).

## Directory Structure & Key Files

### Root Directory
- **`requirements.txt`**: Project dependencies, including `fastapi`, `uvicorn`, `requests`, and `black`. Note: `chromadb` is also required as per imports.

### `data/` Directory
Houses the local SQLite databases and their corresponding ChromaDB vector indices.
- **`enterprise.db`**: The custom HR/Enterprise SQLite database.
- **`chinook.db`**: The classic Chinook music store benchmark database.
- **`enterprise_schema.sql`**: The SQL DDL defining the custom enterprise schema (`departments`, `roles`, `employees`, `project_assignments`).
- **`chroma_db/` & `chroma_db_chinook/`**: Persistent ChromaDB storage directories for the respective databases.

### `pillar1_rag/` Directory
The core implementation of the dynamic RAG and multi-agent SQL pipeline.

- **`dynamic_graph_rag.py`**: Contains the `DynamicSchemaEngine` class.
  - `_reflect_database_schema()`: Extracts FK relationships from SQLite `PRAGMA`.
  - `_auto_ingest_ddl_if_empty()`: Populates ChromaDB with table schemas if empty.
  - `resolve_dependencies_recursive()`: Walks the FK graph up to a specified depth to gather context.
  - `retrieve_optimized_context()`: Combines vector search for the primary table and graph traversal for related tables.

- **`end_to_end_test.py`**: The main interactive CLI orchestrator.
  - Prompts the user to select either the Enterprise DB or Chinook DB.
  - Takes natural language queries in a loop.
  - Implements the 3-Agent pipeline (Retrieve -> Generate -> Validate).
  - Handles the retry mechanism (max 3 retries) and interacts with the local Ollama API (`http://localhost:11434/api/generate`).

- **`insert_dummy_data.py`**: A utility script to populate the `enterprise.db` with mock records for tables like `departments`, `roles`, `employees`, and `project_assignments`.

- **`download_chinook.py` & `create_test_db.py` & `interactive_tester.py`**: Additional utilities for setting up the benchmark environments and isolated testing.

## Technical Stack
- **Language**: Python 3
- **Databases**: SQLite3 (Relational), ChromaDB (Vector)
- **Local LLM Engine**: Ollama (REST API integration via the `requests` library)
- **Default Model**: `phi3` (can be configured in the API call)

## How to use this documentation
For external LLMs analyzing this project, rely on the `DynamicSchemaEngine` for context assembly logic and `end_to_end_test.py` for understanding the prompting and self-correction strategies. The framework relies heavily on correct foreign-key pragmas in SQLite to build its context graph.
