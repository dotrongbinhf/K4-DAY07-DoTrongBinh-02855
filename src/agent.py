from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "No relevant context was found in the knowledge base."

        context_parts: list[str] = []
        for index, result in enumerate(results, start=1):
            metadata = result["metadata"]
            source = (
                metadata.get("source_url")
                or metadata.get("source")
                or metadata.get("doc_id")
                or result["id"]
            )
            context_parts.append(f"[{index}] Source: {source}\n{result['content']}")

        context = "\n\n".join(context_parts)
        prompt = (
            "You answer questions using the knowledge base.\n"
            "Use only the context below. If it is insufficient, say that the information "
            "was not found rather than guessing. Cite the relevant chunks as [1], [2], ...\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )
        return self.llm_fn(prompt)
