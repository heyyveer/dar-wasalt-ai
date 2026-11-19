# DarGlobal–Wasalt AI Assistant

An AI-powered knowledge assistant that answers questions about DarGlobal and Wasalt using publicly available information. The application uses Retrieval-Augmented Generation (RAG) to retrieve relevant information from a curated knowledge base and generate context-aware responses with source references.

**Live Application:** https://dar-wasalt-ai.onrender.com  
**GitHub Repository:** https://github.com/heyyveer/dar-wasalt-ai

## Overview

The DarGlobal–Wasalt AI Assistant enables users to explore company information, real estate projects, and related developments through a conversational interface.

Instead of relying only on an LLM's pre-trained knowledge, the system retrieves relevant information from its indexed dataset before generating an answer.

### Key Features

- Conversational chatbot interface built with Streamlit.
- Knowledge retrieval from DarGlobal and Wasalt data.
- Retrieval-Augmented Generation (RAG) architecture.
- Semantic search using vector embeddings.
- ChromaDB vector database for persistent storage.
- OpenRouter integration for LLM-powered responses.
- Source-aware responses to improve transparency.
- Support for company-related questions and comparisons.
- Out-of-domain query handling.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python 3.11 |
| User Interface | Streamlit |
| LLM Provider | OpenRouter |
| LLM Model | `baidu/ernie-5.5-flash-preview:free` |
| Vector Database | ChromaDB |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) during ingestion |
| Production Query Embeddings | ChromaDB Default ONNX Embedding Function |
| Web Scraping | Requests, BeautifulSoup, Trafilatura |
| Containerization | Docker |
| Deployment | Render |

## System Architecture

The application follows a Retrieval-Augmented Generation architecture.

### Data Ingestion Pipeline

1. Public information is collected from DarGlobal and Wasalt websites.
2. Scraped content is processed and converted into structured documents.
3. Documents are prepared for semantic indexing.
4. Text embeddings are generated during ingestion.
5. Embeddings and associated metadata are stored in ChromaDB.

### Query Processing Pipeline

1. The user submits a question through the Streamlit interface.
2. The query is converted into an embedding.
3. ChromaDB retrieves semantically relevant document chunks.
4. Retrieved context is passed to the LLM through OpenRouter.
5. The LLM generates a response grounded in the retrieved information.
6. The application presents the answer along with relevant source references.

### Architecture Flow

```text
Public Websites
      |
      v
Web Scraping
      |
      v
Data Processing
      |
      v
Text Embeddings
      |
      v
ChromaDB Vector Database
      |
      |
User Query
      |
      v
Streamlit Interface
      |
      v
Query Embedding
      |
      v
Semantic Retrieval
      |
      v
Retrieved Context
      |
      v
OpenRouter LLM
      |
      v
Generated Answer + Sources
```

## Project Structure

```text
dar-wasalt-ai/
│
├── app.py
│
├── chatbot/
│   └── llm.py
│
├── rag/
│   ├── chat.py
│   ├── ingestion.py
│   ├── retrieval.py
│   └── query_router.py
│
├── scraper/
│   ├── darglobal.py
│   ├── discovery.py
│   ├── utils.py
│   └── wasalt.py
│
├── processing/
│   └── document_builder.py
│
├── data/
│   ├── raw/
│   └── processed/
│       └── documents.json
│
├── chroma_db/
│
├── Dockerfile
├── requirements.txt
├── requirements-render.txt
├── .env.example
├── .dockerignore
└── .gitignore
```

## Local Setup

### Prerequisites

- Python 3.11
- Git
- Docker (optional)
- OpenRouter API key

### 1. Clone the Repository

```bash
git clone https://github.com/heyyveer/dar-wasalt-ai.git
cd dar-wasalt-ai
```

### 2. Create a Virtual Environment

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=baidu/ernie-5.5-flash-preview:free
```

Get an API key from [OpenRouter](https://openrouter.ai/).

### 5. Run the Application

```bash
streamlit run app.py
```

The application will be available at:

```text
http://localhost:8501
```

## Docker Setup

Build the Docker image:

```bash
docker build -t dar-wasalt-ai .
```

Run the container:

```bash
docker run -d \
  --name dar-wasalt-container \
  -p 8501:8501 \
  --env-file .env \
  dar-wasalt-ai
```

Open:

```text
http://localhost:8501
```

## Deployment

The application is containerized using Docker and deployed on Render.

**Live URL:** https://dar-wasalt-ai.onrender.com

Production deployment uses a lightweight dependency configuration to reduce container memory usage. ChromaDB's default ONNX embedding function is used for query embeddings, avoiding the need to load the full Sentence Transformers/PyTorch stack during application startup.

Configure the following environment variables in the Render dashboard:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=baidu/ernie-5.5-flash-preview:free
```

## Example Queries

Try asking:

- Tell me about the Rayana project.
- What is DarGlobal?
- Compare DarGlobal and Wasalt.
- What developments are associated with DarGlobal?

## Engineering Considerations

- **Grounded generation:** The LLM receives retrieved context to reduce unsupported answers.
- **Semantic retrieval:** Vector similarity helps retrieve relevant information even when the user's wording differs from the source content.
- **Source transparency:** Retrieved information can be associated with source metadata.
- **Production optimization:** The deployment dependency stack is kept lightweight to reduce memory consumption.
- **Separation of concerns:** Scraping, processing, retrieval, LLM interaction, and UI are maintained in separate modules.

## Future Improvements

- Scheduled data refresh and automated ingestion.
- Hybrid search combining semantic and keyword retrieval.
- Improved reranking for more relevant context.
- Retrieval evaluation and answer-quality metrics.
- Conversation memory and multi-turn context improvements.
- Monitoring for latency, errors, and token usage.

## Author

**Veer Tiwari**

- GitHub: https://github.com/heyyveer
- LinkedIn: https://www.linkedin.com/in/heyveer/
- Portfolio: https://veer-portfolio-nu.vercel.app

---

*Built as an AI-powered knowledge assistant using Python, RAG, ChromaDB, and OpenRouter.*