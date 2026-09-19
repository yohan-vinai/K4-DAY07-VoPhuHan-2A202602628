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
        # TODO: store references to store and llm_fn
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        # TODO: retrieve chunks, build prompt, call llm_fn
        results = self.store.search(question, top_k=top_k)
        context = "\n\n".join(
            f"[Source {index}]\n{result['content']}"
            for index, result in enumerate(results, start=1)
        )
        prompt = (
            "Bạn là trợ lý trả lời câu hỏi dựa trên ngữ cảnh được cung cấp. "
            "Chỉ sử dụng thông tin trong ngữ cảnh; nếu không đủ thông tin, hãy nói rõ "
            "là không tìm thấy câu trả lời trong tài liệu.\n\n"
            f"Ngữ cảnh:\n{context}\n\n"
            f"Câu hỏi: {question}\n"
            "Câu trả lời:"
        )
        return self.llm_fn(prompt)
