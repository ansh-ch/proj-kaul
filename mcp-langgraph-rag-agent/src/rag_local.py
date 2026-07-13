from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = PROJECT_ROOT / "data" / "sample_docs"
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma_db"


def load_documents() -> List[Document]:
    docs = []

    for path in DOCS_DIR.glob("*.txt"):
        text = path.read_text(encoding="utf-8")

        metadata = {
            "source": path.name,
        }

        # Lightweight metadata extraction from our sample files
        for line in text.splitlines():
            if line.startswith("Title:"):
                metadata["title"] = line.replace("Title:", "").strip()
            elif line.startswith("Department:"):
                metadata["department"] = line.replace("Department:", "").strip()
            elif line.startswith("Region:"):
                metadata["region"] = line.replace("Region:", "").strip()

        docs.append(Document(page_content=text, metadata=metadata))

    return docs


def build_vector_store():
    documents = load_documents()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=75,
    )

    chunks = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name="policy_docs",
    )

    print(f"Loaded {len(documents)} documents")
    print(f"Created {len(chunks)} chunks")
    print(f"Persisted Chroma DB to: {CHROMA_DIR}")

    return vector_store


def search(query: str, k: int = 3):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vector_store = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
        collection_name="policy_docs",
    )

    results = vector_store.similarity_search_with_score(query, k=k)

    print(f"\nQuery: {query}\n")

    for i, (doc, score) in enumerate(results, start=1):
        print(f"Result {i}")
        print(f"Score: {score}")
        print(f"Metadata: {doc.metadata}")
        print("Content:")
        print(doc.page_content)
        print("-" * 80)


if __name__ == "__main__":
    build_vector_store()

    search("How many annual leave days do employees in India get?")
    search("What should I do if I receive a phishing email?")
    search("When should travel expenses be submitted?")