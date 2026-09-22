"""Function tool for retrieving grounded information from Vertex AI RAG Corpus."""

import json
import logging
import os

logger = logging.getLogger(__name__)

CORPUS_INFO_FILE = os.path.join(
    os.path.dirname(__file__), "..", "data", "rag_corpus_info.json"
)


def _get_corpus_details() -> tuple[str | None, str]:
    if os.path.exists(CORPUS_INFO_FILE):
        try:
            with open(CORPUS_INFO_FILE, "r") as f:
                data = json.load(f)
                corpus_name = data.get("corpus_name")
                location = data.get("location", "asia-northeast1")
                return corpus_name, location
        except Exception as e:
            logger.error("Failed to read RAG corpus info: %s", e)
    return None, "asia-northeast1"


def consult_herbal_corpus(query: str) -> str:
    """Consult Culpeper's Complete Herbal reference corpus for traditional plant remedies, herbal uses, and historical culinary advice.

    Args:
        query: What to look up (a plant, herb, remedy, or ingredient, e.g. 'thyme', 'garlic', 'mint', 'cough').

    Returns:
        Matched passages from the herbal corpus.
    """
    if not query.strip():
        return "Please provide a search term to consult the herbal corpus."

    corpus_name, location = _get_corpus_details()
    if not corpus_name:
        return "RAG corpus is not configured or still initializing."

    try:
        import vertexai
        from vertexai.preview import rag

        vertexai.init(project="qwiklabs-gcp-01-eb75fbb5d865", location=location)
        resp = rag.retrieval_query(
            text=query.strip(),
            rag_resources=[rag.RagResource(rag_corpus=corpus_name)],
            rag_retrieval_config=rag.RagRetrievalConfig(top_k=3),
        )
        contexts = getattr(resp.contexts, "contexts", [])
        passages = [
            c.text.strip() for c in contexts if getattr(c, "text", "").strip()
        ]
        if passages:
            return "\n\n---\n\n".join(passages)
        return f"No relevant passages found in herbal corpus for '{query}'."
    except Exception as e:
        logger.error("RAG retrieval query error: %s", e)
        return f"Retrieval failed: {e}"
