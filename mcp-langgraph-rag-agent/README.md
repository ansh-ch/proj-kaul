# MCP + LangGraph RAG Agent

A small hands-on project exploring how MCP tools can be used with a LangGraph agent for retrieval, memory, reflection, and evaluation.

The project uses fictional policy documents to demonstrate a basic agentic RAG workflow:

- local document indexing with Chroma
- MCP servers for policy search and memory
- LangGraph for agent orchestration
- simple metadata filtering
- reflection-based lesson storage
- a lightweight evaluation script

The sample policy files are demo/ fictional data only. They do not any company's policies.

## Project structure

```text
src/
  agent_builder.py                 # reusable LangGraph agent builder
  run_agent.py                     # interactive command-line runner
  rag_local.py                     # builds the local Chroma index
  rag_mcp_server.py                # MCP server exposing policy search
  memory_mcp_server.py             # MCP server exposing memory tools
  self_improving_rag_agent.py      # reflection + lesson storage demo
  eval_self_improving_agent.py     # simple evaluation harness

data/
  sample_docs/                     # fictional demo policy documents
```

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_key_here
```

## Run

First build the local vector database:

```bash
python src/rag_local.py
```

Then start the interactive agent:

```bash
python src/run_agent.py
```

You can ask questions such as:

```text
How many annual leave days do employees in India get?
What should I do if I receive a phishing email?
When do I need to submit travel expenses?
```

## Evaluation

Run the basic evaluation script:

```bash
python src/eval_self_improving_agent.py
```

The current evaluation is intentionally simple and checks whether answers contain expected terms. It is meant as a starting point, not a production-grade evaluation framework.

## Notes

This is an educational prototype, not a production system. Some areas that could be improved later:

- semantic memory using embeddings
- reranking retrieved chunks
- hybrid keyword + vector search
- stronger evaluation with an LLM judge
- tracing with LangSmith
- API or UI layer
- Dockerized setup
