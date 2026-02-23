import re
from typing import Any, Dict, List

from rank_bm25 import BM25Okapi


TOKEN_RE = re.compile(r"[a-z0-9]+")


def _normalize(text: str) -> List[str]:
    """
    Normalize text into lowercase alphanumeric tokens.
    Handles: case-insensitivity, extra spaces, punctuation.
    """
    lowered = text.lower().strip()
    return TOKEN_RE.findall(lowered)


class BM25Index:
    """
    BM25 ranking with field-level boosting using rank_bm25 library.
    Name field is weighted higher than description.
    """

    def __init__(self, products: List[Dict[str, Any]]):
        self.products = products
        self.name_boost = 3.0
        self.description_boost = 1.0
        self.brand_boost = 0.5

        self._build_index()

    def _build_index(self) -> None:
        """Build separate BM25 indices for each field."""
        self.name_corpus = []
        self.description_corpus = []
        self.brand_corpus = []

        for product in self.products:
            name = str(product.get("name", ""))
            description = str(product.get("description", ""))
            brand = str(product.get("brand", ""))

            self.name_corpus.append(_normalize(name))
            self.description_corpus.append(_normalize(description))
            self.brand_corpus.append(_normalize(brand))

        self.bm25_name = BM25Okapi(self.name_corpus)
        self.bm25_description = BM25Okapi(self.description_corpus)
        self.bm25_brand = BM25Okapi(self.brand_corpus)

    def search(self, query: str, limit: int = 10) -> List[tuple[float, Dict[str, Any]]]:
        """
        Search products using BM25 with field boosting.
        Returns list of (score, product) tuples, sorted by relevance.
        """
        query_tokens = _normalize(query)

        name_scores = self.bm25_name.get_scores(query_tokens)
        description_scores = self.bm25_description.get_scores(query_tokens)
        brand_scores = self.bm25_brand.get_scores(query_tokens)

        scored: List[tuple[float, Dict[str, Any]]] = []

        for i, product in enumerate(self.products):
            combined_score = (
                name_scores[i] * self.name_boost
                + description_scores[i] * self.description_boost
                + brand_scores[i] * self.brand_boost
            )

            if combined_score > 0:
                scored.append((combined_score, product))

        scored.sort(key=lambda x: (-x[0], x[1].get("id", 0)))
        
        return scored[:limit]
