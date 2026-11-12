Artist GraphRAG
A modular, document-based Graph Retrieval-Augmented Generation
(GraphRAG) application built with Python, LangChain, LangGraph, Google
Gemini, and Neo4j AuraDB.

Artist GraphRAG ingests PDF, DOCX, and TXT documents, extracts entities
and relationships with Gemini, stores the resulting knowledge graph in
Neo4j, retrieves relevant graph information, and generates answers
grounded in the retrieved context.
Project status: The automated test suite most recently reported
63 passed, 0 failed, and 1 dependency deprecation warning.
External Neo4j AuraDB connectivity is a separate integration check and
must be verified in the target environment.

Contents
1. Features
2. Technology stack
3. Architecture
4. Project structure
5. How the application works
6. Installation
7. Configuration
8. Using the CLI
9. Running tests
10. Neo4j graph model
11. Current implementation and
    limitations
12. Security and development
    practices
13. Possible future improvements
1. Features
- Document ingestion, validation, and local storage.
- PDF, DOCX, and TXT text extraction.
- Extracted-text cleaning and normalization.
- Character-based document chunking with overlap.
- Structured entity extraction using LangChain's Gemini integration.
- Structured relationship extraction using Gemini.
- Deterministic graph identifiers and graph mapping.
- Neo4j AuraDB persistence through the Neo4j Python Driver.
- Graph retrieval using Cypher.
- Retrieval-context construction and Gemini answer generation.
- LangGraph-based document-processing and question-answering
  workflows.
- Dependency-injected application construction.
- CLI commands for database checks, document ingestion, and question
  answering.
- Automated tests using mocks for external services where appropriate.
2. Technology stack
  Technology                          Role
  Python                              Main programming language

  LangChain                           LLM integration and structured
model interactions

  langchain-google-genai            Gemini chat-model integration

  LangGraph                           Workflow orchestration for
ingestion and question answering

  Google Gemini                       Entity extraction, relationship
extraction, and answer generation

  Neo4j AuraDB                        Knowledge graph database

  Neo4j Python Driver                 Cypher queries, sessions, and
managed transactions

  Pydantic                            Configuration, request, response,
and graph-model validation

  python-dotenv                     Environment-variable loading

  PyPDF                               PDF text extraction

  python-docx                       DOCX text extraction
pytest                              Automated testing
The current graph storage and retrieval implementation uses the Neo4j
Python Driver directly. LangChain is used for Gemini model interactions,
while LangGraph orchestrates the application workflows.
3. Architecture
The application is organized into focused modules and connected through
dependency injection.
                         ┌──────────────────────┐
                         │    CLI / Application │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┴────────────────┐
                    │                                │
             Document workflow                 QA workflow
                    │                                │
             ┌──────▼──────┐                  ┌──────▼──────┐
             │  Ingestion  │                  │  Retrieval  │
             └──────┬──────┘                  └──────┬──────┘
                    │                                │
             ┌──────▼──────┐                  ┌──────▼──────┐
             │  Document   │                  │ Graph       │
             │  extraction │                  │ retriever   │
             └──────┬──────┘                  └──────┬──────┘
                    │                                │
             ┌──────▼──────┐                         │
             │  Chunking   │                         │
             └──────┬──────┘                         │
                    │                                │
             ┌──────▼──────┐                         │
             │  Knowledge  │                         │
             │  extraction │                         │
             └──────┬──────┘                         │
                    │                                │
             ┌──────▼──────┐                  ┌──────▼──────┐
             │ Graph mapper│                  │ Context     │
             └──────┬──────┘                  │ construction│
                    │                         └──────┬──────┘
             ┌──────▼──────┐                         │
             │ Neo4j graph │                  ┌──────▼──────┐
             │   storage   │                  │ Gemini      │
             └─────────────┘                  │ generation  │
                                              └──────┬──────┘
                                                     │
                                              ┌──────▼──────┐
                                              │   Answer    │
                                              └─────────────┘
Workflow orchestration
The two main workflows are implemented with LangGraph StateGraph:
- Document pipeline: ingestion → document extraction → chunking →
  knowledge extraction → graph storage.
- Question-answering pipeline: graph retrieval →
  generation-request preparation → answer generation.
The factory.py module constructs the clients and services and injects
them into the pipelines and GraphRAGApplication.
4. Project structure
artist_graph_rag/
│
├── .env
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
│
├── data/
│   └── uploads/
│
├── src/
│   └── graphrag_app/
│       ├── __init__.py
│       ├── application.py
│       ├── cli.py
│       ├── config.py
│       ├── factory.py
│       │
│       ├── database/
│       │   ├── __init__.py
│       │   └── neo4j_client.py
│       │
│       ├── ingestion/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── validator.py
│       │   ├── storage.py
│       │   └── service.py
│       │
│       ├── document/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── txt_extractor.py
│       │   ├── pdf_extractor.py
│       │   ├── docx_extractor.py
│       │   ├── extractor.py
│       │   ├── cleaner.py
│       │   └── service.py
│       │
│       ├── chunking/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── strategy.py
│       │   └── service.py
│       │
│       ├── extraction/
│       │   ├── __init__.py
│       │   ├── gemini_client.py
│       │   ├── models.py
│       │   ├── entity_extractor.py
│       │   ├── relationship_extractor.py
│       │   └── service.py
│       │
│       ├── graph/
│       │   ├── __init__.py
│       │   ├── schema.py
│       │   ├── graph_service.py
│       │   ├── mapper.py
│       │   └── ingestion_service.py
│       │
│       ├── retrieval/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── graph_retriever.py
│       │   └── service.py
│       │
│       ├── generation/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   └── answer_generator.py
│       │
│       └── pipeline/
│           ├── __init__.py
│           ├── models.py
│           ├── document_pipeline.py
│           └── qa_pipeline.py
│
├── scripts/
│   └── phase1_demo.py
│
└── tests/
    ├── test_neo4j.py
    ├── test_ingestion.py
    ├── test_document.py
    ├── test_chunking.py
    ├── test_extraction.py
    ├── test_graph_mapper.py
    ├── test_graph_ingestion.py
    ├── test_graph_retriever.py
    ├── test_retrieval_service.py
    ├── test_answer_generator.py
    ├── test_qa_pipeline.py
    ├── test_factory.py
    └── ...
The tree above shows the main application packages and representative
tests. Additional test files may exist in the repository.
Module responsibilities
  Package / file                           Responsibility
  config.py                              Loads and validates Neo4j and
Gemini configuration with Pydantic.

  application.py                         Public application interface,
workflow delegation, and database
lifecycle.

  factory.py                             Constructs and wires services using
dependency injection.

  cli.py                                 CLI parser and command handlers.

  database/neo4j_client.py               Neo4j driver, connectivity checks,
Cypher execution, transactions, and
cleanup.

  ingestion/                             Document validation and storage.

  document/                              TXT, PDF, and DOCX text extraction
and cleaning.

  chunking/                              Character-based splitting and
overlap handling.

  extraction/gemini_client.py            LangChain Gemini chat-model
wrapper.

  extraction/entity_extractor.py         Structured entity extraction.

  extraction/relationship_extractor.py   Structured relationship extraction
and validation.

  graph/mapper.py                        Converts extraction results into
graph models with deterministic
identifiers.

  graph/graph_service.py                 Persists entities and relationships
using parameterized Cypher and
managed transactions.

  retrieval/graph_retriever.py           Queries matching entities and
connected relationships from Neo4j.

  retrieval/service.py                   Builds the context supplied to
answer generation.

  generation/answer_generator.py         Generates an answer from the user's
query and retrieved context.

  pipeline/document_pipeline.py          LangGraph document-ingestion
workflow.
pipeline/qa_pipeline.py                LangGraph retrieval-and-generation
workflow.
5. How the application works
5.1 Document ingestion and graph construction
1. The user supplies a PDF, DOCX, or TXT file.
2. The ingestion service validates the file and stores it in the upload
   directory.
3. The document service extracts and cleans its text.
4. The chunking service divides the text into smaller chunks.
5. Gemini extracts entities from each chunk through the LangChain
   integration.
6. Gemini identifies relationships between the extracted entities.
7. The graph mapper converts extraction results into validated graph
   models and assigns deterministic identifiers.
8. The graph ingestion service stores the entities and relationships in
   Neo4j.
9. The document pipeline returns a result containing the document ID,
   status, chunk count, and graph-storage counts.
5.2 Question answering
1. The user submits a question.
2. The graph retriever searches Neo4j for matching entities and
   connected relationships.
3. The retrieval service formats the retrieved graph data into a
   context string.
4. The QA pipeline prepares a generation request.
5. The answer generator sends the question and retrieved context to
   Gemini.
6. The application returns both the retrieval result and generated
   answer.
The answer is intended to be grounded in the retrieved graph context.
Retrieval quality depends on the entities and relationships present in
Neo4j and on the current lexical retrieval strategy.
5.3 Application construction and lifecycle
create_application() in factory.py creates shared Neo4j and Gemini
clients, constructs the services, and injects them into the document and
QA pipelines.

GraphRAGApplication exposes:
- process_document(request) --- run document ingestion.
- ask(request) --- retrieve knowledge and generate an answer.
- verify_database_connection() --- verify Neo4j connectivity.
- close() --- close the Neo4j driver.
The application supports context-manager usage so that the database
driver is closed when the application scope exits.
6. Installation
The commands below use Windows PowerShell.
Step 1: Open the project directory
cd artist_graph_rag
Step 2: Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
If PowerShell blocks script execution, use an appropriate
execution-policy setting for your environment or activate the
environment through your IDE.
Step 3: Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
The project dependency list should include the packages used by the
current implementation, including neo4j, python-dotenv, pydantic,
pypdf, python-docx, pytest, langchain, langchain-google-genai,
and langgraph. Use the repository's requirements.txt as the
installation source of truth.
Step 4: Configure the Python import path
For the current PowerShell session:
$env:PYTHONPATH = "src"
This makes the graphrag_app package importable without installing the
project as a wheel.
7. Configuration
Create a .env file in the project root. Use the following variable
names:
NEO4J_URI=neo4j+s://YOUR_INSTANCE_ID.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=YOUR_NEO4J_PASSWORD
NEO4J_DATABASE=neo4j

LLM_PROVIDER=gemini
LLM_API_KEY=YOUR_GEMINI_API_KEY
LLM_MODEL=YOUR_SUPPORTED_GEMINI_MODEL
Configuration notes
- Copy the connection URI from your Neo4j AuraDB console.
- Use the AuraDB database username and password.
- Ensure the AuraDB instance is running and reachable from your
  network.
- Use a Gemini API key and a model identifier supported by your
  installed Gemini integration.
- The current configuration accepts gemini as the LLM provider.
- Keep real credentials in .env; never commit this file.
- Keep .env.example populated with placeholder values only.
The application validates required settings during configuration
loading. The Neo4j URI is expected to use the secure neo4j+s://
scheme.
8. Using the CLI
Set the import path before running commands in a new PowerShell session:
$env:PYTHONPATH = "src"
8.1 Display help
python -m graphrag_app.cli --help
8.2 Check Neo4j connectivity
python -m graphrag_app.cli check
A successful check reports that the Neo4j connection succeeded. If it
fails, verify the AuraDB instance status, URI, credentials, network
access, and TLS certificate configuration.
8.3 Ingest a document
python -m graphrag_app.cli ingest "C:\path\to\your\document.pdf"
Supported file extensions:
- .pdf
- .docx
- .txt
The command prints the document name, document ID, processing status,
number of chunks, and graph entity/relationship counts.
8.4 Ask a question
python -m graphrag_app.cli ask "Who is Shiva?"
Limit the number of matching entities:
python -m graphrag_app.cli ask "Who is Shiva?" --top-k 5
Restrict retrieval to a particular document:
python -m graphrag_app.cli ask "Who is Shiva?" --document-id YOUR_DOCUMENT_ID
--top-k must be a positive integer. The CLI validates this argument
before initializing the application.
9. Running tests
Run the full suite from the project root:
$env:PYTHONPATH = "src"
python -m pytest tests/ -v
Run one test module:
python -m pytest tests/test_document.py -v
Show shorter failure details:
python -m pytest tests/ -v --tb=short
Rerun tests that failed in the previous run:
python -m pytest --lf -v
Use python -m pytest if PowerShell cannot find the standalone pytest
executable.
Latest reported test result
The latest full test run reported:
63 passed, 1 warning in 5.33s
The warning came from the installed AnyIO pytest plugin importing
pytest's deprecated CallSpec2 alias. It did not cause a test failure.

Unit tests commonly mock external services. Therefore, a passing
unit-test suite does not by itself prove that the live Gemini API or
Neo4j AuraDB connection is working.
External integration checks
Run the dedicated Neo4j connectivity test if it is present in the
repository:
python .\tests\test_aura_connection.py
A live end-to-end check should separately verify:
1. Neo4j AuraDB connectivity.
2. A Gemini model invocation.
3. Document ingestion and graph persistence.
4. Graph retrieval and answer generation.
10. Neo4j graph model
The current graph uses the Entity node label and the RELATED_TO
relationship type.
Entity nodes
Typical properties:

  Property               Meaning
  id                   Deterministic entity identifier
name                 Entity name
entity_type          Entity category or type
description          Extracted entity description
source_document_id   Source document identifier
source_chunk_id      Source chunk identifier

Additional extracted properties may also be stored when they are
supported by the graph model.
Relationships
Relationships are stored using the Neo4j relationship type RELATED_TO.

Typical properties:

  Property               Meaning
  id                   Relationship identifier
relation_type        Semantic relationship label
description          Extracted relationship description
source_document_id   Source document identifier
source_chunk_id      Source chunk identifier

The semantic relationship label is stored in the relation_type
property. It is not currently represented as a separate Neo4j
relationship type for every semantic relation.

Graph writes use parameterized Cypher. The graph service supports
managed transactions for storing a group of entities and relationships
atomically.
11. Current implementation and limitations
  Area                     Current implementation
  Document formats         PDF, DOCX, TXT
OCR                      Not implemented
Chunking                 Character-based splitting with overlap
LLM integration          LangChain Gemini chat model
Structured extraction    Gemini entity and relationship extraction
Workflow orchestration   LangGraph StateGraph
Graph database           Neo4j AuraDB
Graph persistence        Neo4j Python Driver and Cypher
Graph retrieval          Name/description substring matching
Vector search            Not implemented
Hybrid retrieval         Not implemented
Answer generation        Gemini with retrieved graph context
Frontend                 Not implemented
REST API                 Not implemented
Retrieval limitation
The current retriever uses lexical substring matching against entity
names and descriptions. It does not yet perform embedding-based semantic
similarity, vector search, or hybrid retrieval.

Accordingly, this is a modular graph-based RAG foundation. It should not
yet be described as a vector-based or hybrid GraphRAG implementation.
Integration status
The automated unit tests have passed in the latest reported run. Live
external integration is a separate concern: a successful Neo4j AuraDB
connection and Gemini API invocation must be confirmed in the deployment
environment.
12. Security and development practices
- Store credentials in .env and never commit secrets.
- Keep .env.example limited to placeholder values.
- Keep .env, virtual environments, Python caches, and pytest caches
  out of version control.
- Use the secure neo4j+s:// AuraDB connection scheme.
- Do not disable TLS certificate verification to work around
  connection errors.
- Validate documents before processing.
- Use parameterized Cypher queries rather than interpolating user
  input into query strings.
- Use Pydantic models to validate structured application data.
- Keep database access inside the database package.
- Prefer dependency injection to tightly coupled service construction.
- Add unit tests when introducing or changing behavior.
- Keep live-service integration tests distinct from isolated unit
  tests.
A suitable .gitignore should include at least:
.env
.venv/
venv/
__pycache__/
*.py[cod]
.pytest_cache/
13. Possible future improvements
The modular design provides a foundation for future work such as:
- Embedding generation and Neo4j vector indexes.
- Hybrid retrieval combining lexical, vector, and graph-based search.
- Improved entity resolution across documents and chunks.
- Richer provenance tracking for entities and relationships.
- OCR for scanned PDFs and images.
- More advanced chunking strategies.
- Retrieval evaluation and answer-quality benchmarks.
- REST API and frontend interfaces.
- Authentication, authorization, and deployment configuration.
- Observability, structured logging, and performance monitoring.
These are possible extensions, not claims about currently implemented
features.
Author
Artist GraphRAG

A modular Graph Retrieval-Augmented Generation project built with
Python, LangChain, LangGraph, Google Gemini, and Neo4j AuraDB.