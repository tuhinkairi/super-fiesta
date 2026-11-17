# AI Creative Workspace

An AI-powered creative assistance system designed to help writers organize story information, manage creative references, and generate context-aware suggestions.

The project currently consists of two Python modules:

- **Story Intelligence** – Processes story content, builds a structured knowledge graph, and manages context-aware creative suggestions.
- **Inspiration Ingestion** – Ingests documents, images, and web content, then makes them searchable through semantic search.

---

## Project Architecture

```text
AI-Creative-Workspace/
│
├── modules/
│   ├── __init__.py
│   │
│   ├── story_intelligence/
│   │   ├── knowledge_graph/
│   │   ├── llm/
│   │   │   └── prompts/
│   │   ├── models/
│   │   ├── pipeline/
│   │   ├── suggestion_graph/
│   │   ├── story_rag.py
│   │   ├── config.py
│   │   └── types.py
│   │
│   └── inspiration_ingestion/
│       ├── extractors/
│       ├── ingestion/
│       ├── pipeline/
│       ├── processing/
│       ├── repositories/
│       ├── service.py
│       ├── config.py
│       └── types.py
│
├── storage/                 # Generated locally; not tracked by Git
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 1. Modules Overview

### A. Story Intelligence

The Story Intelligence module analyzes story content and maintains structured story information.

**Key capabilities:**

- Story text processing.
- Character and entity extraction.
- Relationship and event extraction.
- Knowledge graph construction.
- Timeline generation.
- Canonical graph approval.
- Context-aware creative suggestion generation.
- Suggestion approval and rejection with guardrails.

**Public interface:** `StoryRAG`

### B. Inspiration Ingestion

The Inspiration Ingestion module manages external creative references and makes them available for retrieval.

**Key capabilities:**

- PDF, image, TXT, and Markdown ingestion.
- Webpage URL ingestion.
- Text extraction and chunking.
- Embedding generation.
- Metadata storage.
- Semantic search.
- Inspiration retrieval and listing.

**Public interface:** `InspirationService`

---

## 2. Technology Stack

- Python 3.10+
- Google Gemini API
- Google Gen AI SDK
- Pydantic
- Pydantic Settings
- NetworkX
- NumPy
- PyMuPDF
- Pillow
- SQLite-based metadata persistence

See `requirements.txt` for the pinned Python dependencies.

---

## 3. Prerequisites

Before setting up the project, install:

- Python 3.10 or later
- Git
- A Google Gemini API key

---

## 4. Installation and Setup

Follow these steps to set up the project locally.

### Step 1: Clone the repository

```bash
git clone https://github.com/snehapatra791-crypto/AI-Creative-Workspace.git
```

### Step 2: Navigate to the project directory

```bash
cd AI-Creative-Workspace
```

### Step 3: Create a virtual environment

```bash
python -m venv .venv
```

### Step 4: Activate the virtual environment

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

### Step 5: Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5. Environment Configuration

Copy `agents/.env.example` to `agents/.env` (the `agents` project root), then
add your Gemini API key. The shared model settings in this file control the
Story Intelligence, Inspiration Ingestion, and Context-Aware Suggestion modules.

Add the following configuration:

```env
GEMINI_API_KEY=your_gemini_api_key
STORY_MODEL=gemini-3.5-flash
INSPIRATION_MODEL=gemini-3.5-flash
SUGGESTION_MODEL=gemini-3.5-flash
EMBEDDING_MODEL=gemini-embedding-001

# Optional Inspiration Ingestion settings
# STORAGE_DIR=storage
# MAX_FILE_SIZE_MB=20
# CHUNK_SIZE=1000
# CHUNK_OVERLAP=150
```

Replace the placeholder with your own Gemini API key.

**Configuration details:**

| Variable | Description | Default |
|---|---|---|
| `GEMINI_API_KEY` | Gemini API key shared by the three modules | Required |
| `STORY_MODEL` | Model used by Story Intelligence | `gemini-3.5-flash` |
| `INSPIRATION_MODEL` | Model used by Inspiration Ingestion | `gemini-3.5-flash` |
| `SUGGESTION_MODEL` | Model used by Context-Aware Suggestion | `gemini-3.5-flash` |
| `EMBEDDING_MODEL` | Shared dense embedding model | `gemini-embedding-001` |
| `STORAGE_DIR` | Directory for uploaded and processed files | Project `storage/` |
| `MAX_FILE_SIZE_MB` | Maximum allowed upload size | `20` |
| `CHUNK_SIZE` | Text chunk size | `1000` |
| `CHUNK_OVERLAP` | Overlap between text chunks | `150` |

**Important:** Never commit or share your `.env` file or API key. `agents/.env` is excluded through `.gitignore`.

---

## 6. Using the Modules

### A. Story Intelligence – StoryRAG

The `StoryRAG` class provides the main orchestration interface for story processing and creative suggestion generation.

**Example:**

```python
from modules.story_intelligence.story_rag import StoryRAG

with StoryRAG() as rag:

    # Process story content
    result = rag.process_story(
        project_id="project_001",
        story_text="Your story content goes here.",
        chapter_number=1
    )

    # Approve the generated canonical graph
    approved_graph = rag.approve_canonical_graph()

    # Start the suggestion workflow
    rag.start_suggestion_workflow(approved_graph)

    # Generate creative suggestions
    suggestions = rag.generate_suggestions(
        story_context="Describe the scene or creative context.",
        max_suggestions=3
    )

    print(suggestions)
```

**Workflow:**

1. Submit story content for processing.
2. Extract characters, entities, relationships, and events.
3. Generate the canonical knowledge graph.
4. Explicitly approve the canonical graph.
5. Start the suggestion workflow.
6. Generate context-aware creative suggestions.

The canonical graph must be explicitly approved before the suggestion workflow can begin.

### B. Inspiration Ingestion – InspirationService

The `InspirationService` interface provides methods to add and search creative references.

**Example:**

```python
from modules.inspiration_ingestion.service import InspirationService

inspiration = InspirationService()

try:
    # Add a local inspiration file
    result = inspiration.add_file("path/to/reference.pdf")

    # Add a webpage
    webpage = inspiration.add_url("https://example.com")

    # Search references
    results = inspiration.search(
        query="creative writing inspiration",
        top_k=5
    )

    print(results)

finally:
    inspiration.close()
```

**Supported input types:**

- PDF documents
- Images
- TXT files
- Markdown files
- Webpage URLs

The service extracts and processes content, generates embeddings, stores metadata, and supports semantic retrieval.

---

## 7. Integration Between Modules

The two modules are designed to work together through the `StoryRAG` orchestration interface.

StoryRAG provides methods for:

- Adding inspiration files.
- Adding inspiration URLs.
- Searching inspiration references.
- Retrieving relevant creative references for suggestion generation.

The overall workflow connects structured story knowledge with external inspiration to support context-aware creative suggestions.

Both modules can also be used independently through their respective public interfaces.

---

## 8. Testing

The repository contains individual `check_*.py` scripts for checking module components and workflows.

Run an individual check from the project root.

**Example – Story Intelligence:**

```bash
python -m modules.story_intelligence.check_story_rag
```

**Example – Inspiration Ingestion:**

```bash
python -m modules.inspiration_ingestion.check_service
```

Some scripts beginning with `check_live_` require a working Gemini API connection and may make live API requests.

Configure your `.env` file before running those scripts.

---

## 9. Important Notes

- The `.env` file is not included in the repository.
- The Python virtual environment is not included in the repository.
- Generated storage and database files are excluded from Git.
- Each developer should create their own virtual environment.
- Each developer must provide their own Gemini API key.
- Live API tests may consume API quota.

---

## 10. Repository

**GitHub:** [AI-Creative-Workspace](https://github.com/snehapatra791-crypto/AI-Creative-Workspace)

To get the latest version, pull the `main` branch:

```bash
git pull origin main
```

---

*AI Creative Workspace – Supporting structured storytelling and inspiration-driven creativity.*
