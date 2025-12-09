# RAG Template

A production-ready RAG (Retrieval-Augmented Generation) chatbot template built with Clean Architecture principles. Supports both LangChain and LangGraph implementations, FastAPI for REST endpoints, and WebSocket for real-time chat.

## Features

- **Clean Architecture**: Domain-driven design with clear separation of concerns
- **Dual RAG Engines**: Both LangChain and LangGraph implementations (selectable at runtime)
- **FastAPI**: Modern async REST API with automatic OpenAPI documentation
- **WebSocket Support**: Real-time chat functionality
- **Streaming Responses**: Server-Sent Events (SSE) for streaming LLM responses
- **Vector Store**: ChromaDB for document embeddings and similarity search
- **Database**: SQLAlchemy with async support (SQLite by default, easily swappable)
- **Configurable**: Environment-based configuration with sensible defaults
- **Docker Ready**: Containerized deployment with Docker Compose

## Architecture

```text
src/
├── domain/                 # Core business logic (no external dependencies)
│   ├── entities/          # Document, Chunk, Conversation, Message, Query
│   ├── value_objects/     # DocumentMetadata, Embedding, RAGConfig
│   ├── repositories/      # Repository interfaces
│   ├── services/          # Domain services
│   └── exceptions/        # Domain exceptions
│
├── application/           # Application orchestration
│   ├── interfaces/        # External service interfaces (LLM, Embedding, VectorStore)
│   ├── use_cases/         # Business use cases
│   ├── dtos/              # Data transfer objects
│   └── mappers/           # Entity-DTO mappers
│
├── infrastructure/        # External implementations
│   ├── external_services/
│   │   ├── langchain/     # LangChain RAG implementation
│   │   ├── langgraph/     # LangGraph RAG implementation
│   │   └── vector_stores/ # ChromaDB implementation
│   ├── persistence/       # SQLAlchemy models & repositories
│   ├── configuration/     # Settings management
│   └── logging/           # Logging setup
│
├── presentation/          # User interfaces
│   └── api/
│       ├── routes/        # FastAPI routes
│       ├── controllers/   # Request handlers
│       ├── schemas/       # Pydantic schemas
│       └── middleware/    # Error handling, logging
│
└── main.py               # Composition root & entry point
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional)

### Local Development

1. **Clone and setup**

   ```bash
   git clone <repository-url>
   cd RAG_template
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Implement chunking strategy** (required for document ingestion)

   ```python
   # See src/application/interfaces/chunking_strategy.py for the interface
   # You must implement your own chunking strategy
   ```

4. **Run the application**

   ```bash
   python -m src.main
   # Or with hot reload
   uvicorn src.main:create_app --factory --reload
   ```

5. **Access the API**
   - API docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t rag-template .
docker run -p 8000:8000 --env-file .env rag-template
```

## API Endpoints

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/documents` | Ingest a new document |
| GET | `/api/v1/documents` | List all documents |
| DELETE | `/api/v1/documents/{id}` | Delete a document |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat` | Send message, get response |
| POST | `/api/v1/chat/stream` | Send message, stream response (SSE) |
| WS | `/ws/chat` | WebSocket chat |

### Conversations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/conversations` | List all conversations |
| GET | `/api/v1/conversations/{id}` | Get conversation with history |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/ready` | Readiness check |

## Configuration

Configure via environment variables or `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `RAG_IMPLEMENTATION` | `langchain` | RAG engine: `langchain` or `langgraph` |
| `LLM_PROVIDER` | `openai` | LLM provider: `openai` or `anthropic` |
| `OPENAI_API_KEY` | - | OpenAI API key |
| `ANTHROPIC_API_KEY` | - | Anthropic API key |
| `LLM_MODEL` | `gpt-4` | LLM model name |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/rag.db` | Database connection string |
| `CHROMA_PERSIST_DIRECTORY` | `./data/chroma` | ChromaDB storage path |
| `API_PORT` | `8000` | API server port |
| `DEBUG` | `false` | Enable debug mode |

## Implementing Chunking Strategy

The template requires you to implement your own chunking strategy. Create a class implementing `IChunkingStrategy`:

```python
from src.application.interfaces.chunking_strategy import IChunkingStrategy
from src.domain.entities.document import Document
from src.domain.entities.chunk import Chunk

class MyChunkingStrategy(IChunkingStrategy):
    @property
    def strategy_name(self) -> str:
        return "my_strategy"

    async def chunk_document(self, document: Document) -> list[Chunk]:
        # Implement your chunking logic here
        pass

    def get_config(self) -> dict:
        return {"chunk_size": 1000, "overlap": 200}
```

Then register it in `main.py`:

```python
container.set_chunking_strategy(MyChunkingStrategy())
```

## Switching RAG Engines

### Via Configuration

Set `RAG_IMPLEMENTATION=langgraph` in your `.env` file.

### Per Request

Include `implementation` in your chat request:

```json
{
  "message": "What is RAG?",
  "config": {
    "implementation": "langgraph",
    "top_k": 5
  }
}
```

## Development

### Project Structure

- **Domain Layer**: Pure business logic, no external dependencies
- **Application Layer**: Use cases and service interfaces
- **Infrastructure Layer**: External service implementations
- **Presentation Layer**: API endpoints and schemas

### Adding New Features

1. Define domain entities/value objects in `src/domain/`
2. Create interfaces in `src/application/interfaces/`
3. Implement use cases in `src/application/use_cases/`
4. Add infrastructure implementations in `src/infrastructure/`
5. Expose via API in `src/presentation/api/`
