import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MEMORY_FILE = PROJECT_ROOT / "data" / "memory_store.json"

mcp = FastMCP("memory-server")


STOPWORDS = {
    "a", "an", "the",
    "and", "or", "but",
    "is", "are", "was", "were", "be", "being", "been",
    "to", "of", "for", "from", "in", "on", "at", "by", "with",
    "about", "as", "into", "over", "after", "before",
    "what", "when", "where", "why", "how",
    "i", "me", "my", "we", "our", "you", "your",
    "do", "does", "did", "should", "can", "could", "would",
    "get", "give", "tell", "answer",
}


def tokenize(text: str) -> set[str]:
    """
    Convert text into normalized whole-word tokens.
    Removes common stopwords and very short terms.
    """
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_]*\b", text.lower())

    return {
        word
        for word in words
        if word not in STOPWORDS and len(word) >= 3
    }


def load_memories() -> list[dict]:
    if not MEMORY_FILE.exists():
        return []

    text = MEMORY_FILE.read_text(encoding="utf-8").strip()

    if not text:
        return []

    return json.loads(text)


def save_memories(memories: list[dict]) -> None:
    MEMORY_FILE.write_text(
        json.dumps(memories, indent=2),
        encoding="utf-8",
    )


@mcp.tool()
def save_memory(
    memory_type: str,
    content: str,
    source: Optional[str] = None,
) -> str:
    """
    Save a useful memory for future agent runs.

    Use this tool to store reusable lessons, user preferences, failed approaches,
    successful strategies, or facts that should influence future responses.

    Arguments:
    - memory_type: Category of memory. Examples: preference, lesson, correction, strategy.
    - content: The memory content to store.
    - source: Optional source of the memory, such as user_feedback or agent_reflection.
    """

    memories = load_memories()

    new_memory = {
        "id": len(memories) + 1,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "memory_type": memory_type,
        "content": content,
        "source": source or "unspecified",
    }

    memories.append(new_memory)
    save_memories(memories)

    return f"Saved memory {new_memory['id']}: {content}"


@mcp.tool()
def search_memory(query: str, memory_type: Optional[str] = None, k: int = 5) -> str:
    """
    Search stored memories using whole-word keyword matching.

    Use this tool before answering when prior user preferences, lessons,
    corrections, or strategies may be relevant.

    Arguments:
    - query: Search query.
    - memory_type: Optional filter. Examples: preference, lesson, correction, strategy.
    - k: Maximum number of memories to return.
    """

    memories = load_memories()
    query_tokens = tokenize(query)

    if not query_tokens:
        return "No searchable terms found in query."

    scored_memories = []

    for memory in memories:
        if memory_type and memory.get("memory_type") != memory_type:
            continue

        searchable_text = (
            f"{memory.get('memory_type', '')} "
            f"{memory.get('content', '')} "
            f"{memory.get('source', '')}"
        )

        memory_tokens = tokenize(searchable_text)

        matched_tokens = query_tokens.intersection(memory_tokens)
        score = len(matched_tokens)

        if score > 0:
            scored_memories.append((score, matched_tokens, memory))

    scored_memories.sort(key=lambda x: x[0], reverse=True)

    top_memories = scored_memories[:k]

    if not top_memories:
        return "No relevant memories found."

    output_parts = []

    for score, matched_tokens, memory in top_memories:
        output_parts.append(
            f"""
Memory ID: {memory.get("id")}
Type: {memory.get("memory_type")}
Source: {memory.get("source")}
Timestamp: {memory.get("timestamp")}
Relevance score: {score}
Matched terms: {", ".join(sorted(matched_tokens))}
Content: {memory.get("content")}
""".strip()
        )

    return "\n\n---\n\n".join(output_parts)


@mcp.tool()
def list_memories() -> str:
    """
    List all stored memories.

    Use this tool when debugging or reviewing what the agent has learned.
    """

    memories = load_memories()

    if not memories:
        return "No memories stored yet."

    output_parts = []

    for memory in memories:
        output_parts.append(
            f"""
Memory ID: {memory.get("id")}
Type: {memory.get("memory_type")}
Source: {memory.get("source")}
Timestamp: {memory.get("timestamp")}
Content: {memory.get("content")}
""".strip()
        )

    return "\n\n---\n\n".join(output_parts)


if __name__ == "__main__":
    mcp.run(transport="stdio")