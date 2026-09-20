"""Run the Lab 7 retrieval benchmark on the verified Tiki policy corpus.

Usage (PowerShell):
    python bench.py

The script deliberately defaults to MockEmbedder, so it never spends API
credits. Its scores are structural demonstrations only; switch the `embedder`
assignment in `main()` to a real embedding backend before making semantic
quality claims.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from src.chunking import (
    ChunkingStrategyComparator,
    FixedSizeChunker,
    RecursiveChunker,
    SentenceChunker,
)
from src.embeddings import MockEmbedder, OpenAIEmbedder
from src.models import Document
from src.agent import KnowledgeBaseAgent
from src.store import EmbeddingStore


CORPUS_DIR = Path("data/tiki-doi-tra")
OUTPUT_PATH = Path("ket_qua_benchmark.txt")
CACHE_PATH = Path(".cache/embedding_cache.json")
CHUNK_SIZE = 500

BENCHMARKS = [
    {
        "query": "Chương trình đổi trả 365 ngày áp dụng cho ngành hàng và nhà bán nào?",
        "gold_doc_id": "tiki-doi-tra-365",
        "must_contain": ("Điện gia dụng", "Thiết bị số", "Tiki Trading"),
        "metadata_filter": None,
    },
    {
        "query": "Khi từ chối yêu cầu đổi trả hoặc bảo hành, nhà bán Dropship cần cung cấp những loại bằng chứng hợp lệ nào?",
        "gold_doc_id": "tiki-dropship-doi-tra-bao-hanh",
        "must_contain": ("biên bản bàn giao", "ảnh hoặc video", "biên bản thẩm định"),
        "metadata_filter": None,
    },
    {
        "query": "Nhà bán mô hình NGON cần làm gì khi hàng hoàn bị hư hỏng do lỗi vận chuyển?",
        "gold_doc_id": "tiki-ngon-doi-tra-boi-thuong",
        "must_contain": ("24 giờ", "bồi thường"),
        "metadata_filter": None,
    },
    {
        "query": "Nhà bán FBT phải sắp xếp rút hàng trong thời hạn bao lâu?",
        "gold_doc_id": "tiki-fbt-doi-tra-bao-hanh",
        "must_contain": ("32 ngày làm việc",),
        "metadata_filter": None,
    },
    {
        "query": "Thời hạn đổi trả miễn phí là bao lâu?",
        "gold_doc_id": "tiki-doi-tra-30-ngay",
        "must_contain": ("30 ngày",),
        "metadata_filter": {"audience": "buyer"},
    },
]


class Reporter:
    """Print benchmark output and retain exactly the same text for the report file."""

    def __init__(self) -> None:
        self.lines: list[str] = []

    def log(self, message: str = "") -> None:
        print(message)
        self.lines.append(message)

    def save(self, path: Path) -> None:
        path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")


class CachedEmbedder:
    """Cache embeddings by backend name and text hash to avoid repeat API calls."""

    def __init__(self, embedder: Any, cache_path: Path = CACHE_PATH) -> None:
        self._embedder = embedder
        self._backend_name = getattr(embedder, "_backend_name", embedder.__class__.__name__)
        self._cache_path = cache_path
        try:
            self._cache: dict[str, list[float]] = json.loads(cache_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            self._cache = {}

    def __call__(self, text: str) -> list[float]:
        key = hashlib.sha256(f"{self._backend_name}\0{text}".encode("utf-8")).hexdigest()
        if key not in self._cache:
            self._cache[key] = self._embedder(text)
        return self._cache[key]

    def save(self) -> None:
        self._cache_path.parent.mkdir(exist_ok=True)
        self._cache_path.write_text(
            json.dumps(self._cache, ensure_ascii=False), encoding="utf-8"
        )


class HeadingChunker:
    """Chunk Markdown by headings and keep that heading on every child chunk."""

    heading_pattern = re.compile(r"(?m)^#{1,6}\s+.+$")

    def __init__(self, chunk_size: int = CHUNK_SIZE) -> None:
        self.chunk_size = chunk_size
        self._fallback = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        sections = re.split(r"(?m)(?=^#{1,6}\s+.+$)", text.strip())
        chunks: list[str] = []
        for section in sections:
            section = section.strip()
            if not section:
                continue

            heading_match = self.heading_pattern.match(section)
            if heading_match is None:
                chunks.extend(self._fallback.chunk(section))
                continue

            heading = heading_match.group(0)
            body = section[heading_match.end() :].strip()
            complete_section = f"{heading}\n{body}".strip()
            if len(complete_section) <= self.chunk_size:
                chunks.append(complete_section)
                continue

            available_size = max(1, self.chunk_size - len(heading) - 1)
            body_chunks = RecursiveChunker(chunk_size=available_size).chunk(body)
            chunks.extend(f"{heading}\n{body_chunk}" for body_chunk in body_chunks)
        return chunks


def parse_markdown(path: Path) -> tuple[dict[str, str], str]:
    """Read the small YAML-like frontmatter format used by this lab corpus."""
    raw_text = path.read_text(encoding="utf-8")
    if not raw_text.startswith("---\n"):
        return {}, raw_text.strip()

    _, separator, remainder = raw_text.partition("\n---\n")
    if not separator:
        raise ValueError(f"Frontmatter is not closed in {path}")

    frontmatter, _, content = raw_text[4:].partition("\n---\n")
    metadata: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, value = line.split(":", maxsplit=1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")
    return metadata, content.strip()


def load_corpus(chunker: Any) -> tuple[list[Document], list[str]]:
    """Parse every verified policy file and turn each chunk into a Document."""
    documents: list[Document] = []
    bodies: list[str] = []
    for path in sorted(CORPUS_DIR.glob("*.md")):
        metadata, body = parse_markdown(path)
        if not body:
            continue
        bodies.append(body)
        doc_id = metadata.get("doc_id", path.stem)
        for index, content in enumerate(chunker.chunk(body)):
            documents.append(
                Document(
                    id=f"{path.stem}#{index}",
                    content=content,
                    metadata={**metadata, "doc_id": doc_id, "file_name": path.name},
                )
            )
    return documents, bodies


def report_baseline(reporter: Reporter, bodies: list[str]) -> None:
    """Compare the three supplied strategies on the first three policy documents."""
    baseline_text = "\n\n".join(bodies[:3])
    comparison = ChunkingStrategyComparator().compare(baseline_text, chunk_size=CHUNK_SIZE)
    reporter.log("=== Baseline on the first 3 policy documents (frontmatter excluded) ===")
    for name, stats in comparison.items():
        reporter.log(
            f"{name}: count={stats['count']}, avg_length={stats['avg_length']:.2f}"
        )


def report_results(
    reporter: Reporter,
    store: EmbeddingStore,
    benchmark: dict[str, Any],
    number: int,
    agent: KnowledgeBaseAgent | None = None,
) -> None:
    """Print top-3 results and whether their text contains the declared gold answer."""
    query = benchmark["query"]
    results = store.search(query, top_k=3)
    reporter.log(f"\n=== Query {number}: {query} ===")
    reporter.log("Run: no metadata filter")
    _print_top_results(reporter, results, benchmark)

    metadata_filter = benchmark["metadata_filter"]
    if metadata_filter is not None:
        filtered_results = store.search_with_filter(
            query, top_k=3, metadata_filter=metadata_filter
        )
        reporter.log(f"Run: metadata_filter={metadata_filter}")
        _print_top_results(reporter, filtered_results, benchmark)

    if agent is not None:
        answer = agent.answer(query, top_k=3, metadata_filter=metadata_filter)
        reporter.log(f"Agent answer: {answer}")


def _print_top_results(
    reporter: Reporter, results: list[dict[str, Any]], benchmark: dict[str, Any]
) -> None:
    if not results:
        reporter.log("  No matching chunks.")
        return

    for rank, result in enumerate(results, start=1):
        content = result["content"].replace("\n", " ")
        preview = content[:180] + ("..." if len(content) > 180 else "")
        is_gold_document = result["metadata"].get("doc_id") == benchmark["gold_doc_id"]
        has_answer_text = all(term in result["content"] for term in benchmark["must_contain"])
        reporter.log(
            f"  Top-{rank}: score={result['score']:.4f} | "
            f"doc_id={result['metadata'].get('doc_id')} | "
            f"gold_doc={is_gold_document} | contains_gold_text={has_answer_text}"
        )
        reporter.log(f"         {preview}")


def make_chunker(strategy: str) -> Any:
    if strategy == "fixed":
        return FixedSizeChunker(chunk_size=CHUNK_SIZE, overlap=50)
    if strategy == "sentence":
        return SentenceChunker(max_sentences_per_chunk=3)
    if strategy == "recursive":
        return RecursiveChunker(chunk_size=CHUNK_SIZE)
    return HeadingChunker(chunk_size=CHUNK_SIZE)


def make_embedder(provider: str) -> CachedEmbedder:
    if provider == "mock":
        return CachedEmbedder(MockEmbedder())

    load_dotenv(override=False)
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required for --provider openai")
    model_name = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    return CachedEmbedder(OpenAIEmbedder(model_name=model_name))


def make_openai_llm_fn() -> tuple[str, Any]:
    """Build the chat callable injected into KnowledgeBaseAgent for CP6."""
    from openai import OpenAI

    load_dotenv(override=False)
    model_name = os.getenv("OPENAI_CHAT_MODEL")
    if not model_name:
        raise RuntimeError("OPENAI_CHAT_MODEL is required for --with-agent")
    client = OpenAI()

    def llm_fn(prompt: str) -> str:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return response.choices[0].message.content or ""

    return model_name, llm_fn


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Lab 7 retrieval benchmark.")
    parser.add_argument("--provider", choices=("mock", "openai"), default="mock")
    parser.add_argument(
        "--strategy", choices=("fixed", "sentence", "recursive", "heading"), default="heading"
    )
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument(
        "--with-agent",
        action="store_true",
        help="Call OPENAI_CHAT_MODEL through KnowledgeBaseAgent for each query.",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if not CORPUS_DIR.exists():
        raise FileNotFoundError(f"Missing benchmark corpus: {CORPUS_DIR}")

    reporter = Reporter()
    chunker = make_chunker(args.strategy)
    documents, bodies = load_corpus(chunker)
    embedder = make_embedder(args.provider)
    store = EmbeddingStore(collection_name="tiki_returns_benchmark", embedding_fn=embedder)
    store.add_documents(documents)
    agent = None

    reporter.log("Lab 7 retrieval benchmark — Tiki return/warranty policies")
    reporter.log(f"Embedding backend: {embedder._backend_name}")
    reporter.log(f"Chunker: {chunker.__class__.__name__}(chunk_size={CHUNK_SIZE})")
    reporter.log(f"Files loaded: {len(bodies)}")
    reporter.log(f"Chunks loaded: {store.get_collection_size()}")
    if args.with_agent:
        model_name, llm_fn = make_openai_llm_fn()
        agent = KnowledgeBaseAgent(store=store, llm_fn=llm_fn)
        reporter.log(f"Chat model: {model_name}")
    report_baseline(reporter, bodies)
    for number, benchmark in enumerate(BENCHMARKS, start=1):
        report_results(reporter, store, benchmark, number, agent=agent)

    reporter.save(args.output)
    embedder.save()
    reporter.log(f"\nSaved full output to: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
