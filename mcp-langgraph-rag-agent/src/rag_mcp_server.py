from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma_db"

mcp = FastMCP("rag-policy-server")


VALID_DEPARTMENTS = {
    "hr": "HR",
    "human resources": "HR",
    "it": "IT",
    "technology": "IT",
    "information technology": "IT",
    "finance": "Finance",
    "travel": "Finance",
}

VALID_REGIONS = {
    "india": "India",
    "indian": "India",
    "global": "Global",
    "worldwide": "Global",
}


def normalize_department(department: Optional[str]) -> Optional[str]:
    if not department:
        return None

    normalized = department.strip().lower()
    return VALID_DEPARTMENTS.get(normalized, department.strip())


def normalize_region(region: Optional[str]) -> Optional[str]:
    if not region:
        return None

    normalized = region.strip().lower()
    return VALID_REGIONS.get(normalized, region.strip())


def get_vector_store():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    return Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
        collection_name="policy_docs",
    )


def build_metadata_filter(
    department: Optional[str] = None,
    region: Optional[str] = None,
):
    filter_conditions = []

    department = normalize_department(department)
    region = normalize_region(region)

    if department:
        filter_conditions.append({"department": {"$eq": department}})

    if region:
        filter_conditions.append({"region": {"$eq": region}})

    if len(filter_conditions) == 1:
        return filter_conditions[0]

    if len(filter_conditions) > 1:
        return {"$and": filter_conditions}

    return None


@mcp.tool()
def search_policy_docs(
    query: str,
    department: Optional[str] = None,
    region: Optional[str] = None,
    k: int = 3,
) -> str:
    """
    Search company policy documents using semantic similarity and optional metadata filters.

    Use this tool when the user asks about company policy, HR, leave, annual leave,
    parental leave, IT security, phishing, MFA, travel, reimbursement, expenses,
    finance policy, or internal rules.

    Arguments:
    - query: The natural-language search query.
    - department: Optional metadata filter. Allowed values: HR, IT, Finance.
      Use HR for leave, parental leave, annual leave, employee benefits.
      Use IT for security, phishing, passwords, MFA, laptops.
      Use Finance for travel, reimbursement, expenses, hotels, meals.
    - region: Optional metadata filter. Allowed values: India, Global.
      Use India when the user asks about India-specific policies.
      Use Global for global policies.
    - k: Number of chunks to retrieve, usually 3.
    """

    vector_store = get_vector_store()
    metadata_filter = build_metadata_filter(department=department, region=region)

    if metadata_filter:
        results = vector_store.similarity_search(
            query=query,
            k=k,
            filter=metadata_filter,
        )
    else:
        results = vector_store.similarity_search(
            query=query,
            k=k,
        )

    if not results:
        return (
            "No relevant policy documents found for the given query and metadata filters. "
            f"Filters used: department={department}, region={region}."
        )

    output_parts = []

    for i, doc in enumerate(results, start=1):
        metadata = doc.metadata

        output_parts.append(
            f"""
Result {i}
Source: {metadata.get("source", "unknown")}
Title: {metadata.get("title", "unknown")}
Department: {metadata.get("department", "unknown")}
Region: {metadata.get("region", "unknown")}

Content:
{doc.page_content}
""".strip()
        )

    return "\n\n---\n\n".join(output_parts)


if __name__ == "__main__":
    mcp.run(transport="stdio")