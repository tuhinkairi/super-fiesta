# Context-Aware Suggestion RAG

A modular, context-aware recommendation system that combines user-provided documents with external intelligence sources to generate relevant, actionable content suggestions.

The project uses Retrieval-Augmented Generation (RAG), hybrid search, contextual analysis, and configurable AI services to help generate suggestions grounded in both document context and current information.

> **Project status:** Core modules, service abstractions, and integration components are implemented. Live third-party API compatibility and complete end-to-end workflow verification are still ongoing.

---

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Architecture](#architecture)
4. [Technology Stack](#technology-stack)
5. [Project Structure](#project-structure)
6. [Installation](#installation)
7. [Environment Configuration](#environment-configuration)
8. [Core Components](#core-components)
9. [Testing](#testing)
10. [Current Limitations](#current-limitations)
11. [Future Improvements](#future-improvements)

---

## Overview

Context-Aware Suggestion RAG is designed to analyze uploaded documents, extract meaningful context, collect relevant external information, and use retrieval-based intelligence to support content recommendations.

The intended workflow is:

1. Accept user documents.
2. Extract and preprocess document content.
3. Identify topics, keywords, entities, and summaries.
4. Collect relevant trends and news.
5. Generate dense and sparse embeddings.
6. Store document representations in a vector database.
7. Retrieve relevant information using hybrid search.
8. Generate and rank contextual recommendations.
9. Produce content using an LLM.

The architecture is modular, allowing individual providers and services to be replaced without redesigning the entire system.

## Key Features

### Document Processing
- PDF, DOCX, TXT, and JSON ingestion.
- Text extraction and preprocessing.
- Configurable document chunking.
- Document metadata and chunk management.

### Context Intelligence
- Topic extraction.
- Keyword extraction.
- Named-entity extraction.
- Extractive document summarization.
- Context analysis and merging.

### External Intelligence
- Google Trends integration.
- RSS-based news collection.
- Configurable intelligence providers.
- Region- and language-aware collection.

### Embedding and Retrieval
- Dense embeddings.
- Sparse embeddings.
- Hybrid vector retrieval.
- Metadata filtering.
- Reciprocal Rank Fusion.
- Optional reranking interface.

### Recommendation Engine
- Recommendation generation.
- Relevance scoring.
- Recommendation ranking.
- Filtering and diversification.
- Recommendation validation.

### AI Content Generation
- Gemini provider abstraction.
- Configurable generation parameters.
- Prompt templates.
- Output validation and formatting.

### Supporting Infrastructure
- Configuration validation.
- Caching.
- Security utilities.
- Logging and observability.
- Workflow orchestration abstractions.
- Reusable utility modules.

---

## Architecture

The project follows a modular, service-oriented architecture.

```text
                    USER DOCUMENTS
                          |
                          v
                  DOCUMENT INGESTION
                          |
                          v
                   CONTEXT EXTRACTION
                          |
                          v
                  CONTEXT INTELLIGENCE
                          |
             +------------+------------+
             |                         |
             v                         v
       GOOGLE TRENDS              NEWS SOURCES
             |                         |
             +------------+------------+
                          |
                          v
                  EMBEDDING SERVICE
                          |
                    +-----+-----+
                    |           |
                    v           v
                  DENSE       SPARSE
                 EMBEDDING   EMBEDDING
                    |           |
                    +-----+-----+
                          |
                          v
                   PINECONE VECTOR DB
                          |
                          v
                    HYBRID RETRIEVAL
                          |
                          v
                 RECOMMENDATION ENGINE
                          |
                          v
                    GEMINI LLM
                          |
                          v
                 GENERATED SUGGESTIONS
```

The diagram represents the intended processing flow. The complete end-to-end orchestration and live provider integrations are subject to further verification.

## Technology Stack

| Category | Technology |
|---|---|
| Language | Python 3.11+ |
| LLM | Google Gemini |
| Embeddings | Google embedding provider |
| Vector Database | Pinecone |
| Orchestration | LangGraph |
| Document Processing | PyPDF, python-docx |
| Configuration | Pydantic, Pydantic Settings |
| HTTP Client | HTTPX |
| News Collection | Feedparser |
| Retry Handling | Tenacity |
| Testing | Pytest |
| Environment Management | python-dotenv |

---

## Project Structure

```text
context_aware_suggestion_pipeline/
│
├── src/
│   └── context_aware_suggestion_rag/
│       │
│       ├── __init__.py
│       ├── pipeline.py
│       ├── facade.py
│       ├── exceptions.py
│       ├── constants.py
│       │
│       ├── config/
│       ├── core/
│       ├── domain/
│       ├── ingestion/
│       ├── context/
│       ├── intelligence/
│       ├── embeddings/
│       ├── database/
│       ├── retrieval/
│       ├── recommendation/
│       ├── generation/
│       ├── llm/
│       ├── workflows/
│       ├── interfaces/
│       ├── cache/
│       ├── security/
│       ├── observability/
│       └── utils/
│
├── tests/
├── examples/
├── scripts/
├── config/
│
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── README.md
└── LICENSE
```

### Module Responsibilities

| Module | Responsibility |
|---|---|
| `config` | Application and provider configuration |
| `core` | Shared types, protocols, validation, logging |
| `domain` | Domain entities, schemas, and business rules |
| `ingestion` | Document loading, extraction, chunking |
| `context` | Context extraction, analysis, summarization |
| `intelligence` | Trends and news collection |
| `embeddings` | Dense and sparse embedding generation |
| `database` | Pinecone connection and vector storage |
| `retrieval` | Dense, sparse, and hybrid retrieval |
| `recommendation` | Suggestion generation, scoring, ranking |
| `generation` | Content generation and formatting |
| `llm` | LLM provider integration |
| `workflows` | Workflow definitions and execution |
| `interfaces` | Provider and service contracts |
| `cache` | Caching abstractions and implementations |
| `security` | Input validation, access control, sanitization |
| `observability` | Metrics, tracing, event logging |
| `utils` | Reusable helper utilities |

---

## Installation

### Prerequisites

- Python 3.11 or newer.
- pip.
- A Google Gemini API key for live LLM and embedding operations.
- A Pinecone account and API key for vector database operations.

### 1. Clone the repository

```powershell
git clone <YOUR_REPOSITORY_URL>
cd context_aware_suggestion_pipeline
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### 4. Install the project

For development:

```powershell
pip install -e ".[dev]"
```

Alternatively, install dependencies using:

```powershell
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 5. Verify installation

```powershell
python -c "import context_aware_suggestion_rag; print(context_aware_suggestion_rag.__version__)"
```

---

## Environment Configuration

Create a local `.env` file using `.env.example` as a template.

Example:

```env
# Gemini
GEMINI_API_KEY=your_gemini_api_key

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key

# Application
CASR_ENVIRONMENT=development
CASR_DEBUG=true
CASR_LOG_LEVEL=INFO
```

Additional settings are available through the configuration modules.

**Important:**
- Never commit `.env` files.
- Never expose API keys in source code.
- Keep secrets outside version control.
- Ensure the Pinecone index dimension matches the configured dense embedding dimension.
- Verify provider model identifiers against the currently supported API models before live deployment.

---

## Core Components

### 1. Document Ingestion

The ingestion module supports loading and processing:

- PDF
- DOCX
- TXT
- JSON

Documents are extracted, validated, and divided into manageable chunks for downstream processing.

### 2. Context Extraction

The context module identifies useful information from document text, including:

- Topics.
- Keywords.
- Named entities.
- Extractive summaries.

The extracted context can be used to construct search queries and guide intelligence collection.

### 3. Intelligence Collection

The intelligence module provides provider abstractions for collecting:

- Google Trends information.
- RSS news articles.

Collection can be configured using region, language, query, and result limits.

### 4. Embedding Service

The embedding module provides:

- Dense embedding generation.
- Sparse embedding generation.
- Batch embedding operations.
- Hybrid embedding representations.

Provider implementations can be replaced through the embedding abstractions.

### 5. Vector Database

The database module provides Pinecone-oriented components for:

- Index management.
- Vector insertion.
- Vector querying.
- Namespace management.
- Vector deletion.
- Repository-level operations.

### 6. Retrieval

The retrieval module supports:

- Dense retrieval.
- Sparse retrieval.
- Hybrid retrieval.
- Reciprocal Rank Fusion.
- Optional reranking through an abstraction.

### 7. Recommendation

The recommendation module provides:

- Candidate generation.
- Scoring.
- Ranking.
- Filtering.
- Diversification.
- Validation.

### 8. Generation

The generation module provides prompt construction, LLM-backed generation adapters, output validation, and formatting.

### 9. Pipeline and Facade

The root pipeline and facade modules provide the generic pipeline execution and public package interface.

The complete application workflow will be connected and verified as the remaining integration work progresses.

---

## Testing

The project uses Pytest.

Run the complete test suite:

```powershell
python -m pytest tests/ -v
```

Run with coverage:

```powershell
python -m pytest tests/ --cov=context_aware_suggestion_rag --cov-report=term-missing
```

Run an individual test file:

```powershell
python -m pytest tests/test_config_integration.py -v
```

Run a specific test:

```powershell
python -m pytest tests/test_security_service.py::test_health_check -v
```

Tests using external services should use controlled test credentials or mocks. A passing unit or integration test with mocked providers does not establish that a live external API is working.

---

## Current Limitations

The following areas require additional implementation or verification before production deployment:

1. Full end-to-end workflow integration.
2. Live Gemini model and SDK compatibility verification.
3. Live Pinecone index and hybrid query verification.
4. Sparse embedding model and provider compatibility.
5. Retrieval fusion configuration alignment.
6. Concrete reranker integration.
7. Recommendation scoring configuration integration.
8. Production-level security and reliability review.
9. External provider failure handling and operational monitoring.

---

## Future Improvements

- Complete end-to-end orchestration.
- Improve retrieval relevance and reranking.
- Add configurable recommendation strategies.
- Expand external intelligence providers.
- Add multilingual document and content support.
- Improve observability and performance monitoring.
- Add production deployment configurations.
- Add comprehensive live API integration tests.

---

## Contributing

Contributions, bug reports, and suggestions are welcome.

When contributing:

1. Follow the existing modular architecture.
2. Keep provider implementations replaceable.
3. Add tests for new functionality.
4. Avoid committing credentials or environment files.
5. Run the test suite before submitting changes.

---

## License

See the [LICENSE](LICENSE) file for licensing information.

---

**Context-Aware Suggestion RAG**  
*A modular foundation for context-driven intelligence and content recommendations.*