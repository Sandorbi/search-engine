import hashlib
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.constants import (
    BRAND_FIELD_WEIGHT,
    DESCRIPTION_FIELD_WEIGHT,
    EMBEDDING_BATCH_SIZE,
    LEXICAL_WEIGHT,
    MIN_TOP_SCORE,
    NAME_FIELD_WEIGHT,
    SEMANTIC_MODEL_NAME,
    SEMANTIC_WEIGHT,
)

TOKEN_RE = re.compile(r"[a-z0-9]+")


def _normalize(text: str) -> list[str]:
    """
    Normalize text into lowercase alphanumeric tokens.
    """
    lowered = text.lower().strip()
    return TOKEN_RE.findall(lowered)


class HybridSearchIndex:
    """
    Hybrid search combining BM25 and semantic embeddings.
    """

    def __init__(self, products: list[dict[str, Any]]):
        print(f"Loading hybrid search index for {len(products)} products...")
        self.products = products
        self.name_boost = NAME_FIELD_WEIGHT
        self.description_boost = DESCRIPTION_FIELD_WEIGHT
        self.brand_boost = BRAND_FIELD_WEIGHT

        self._build_lexical_index()
        self._build_semantic_index()

    def _build_lexical_index(self) -> None:
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

    def _build_semantic_index(self) -> None:
        """Build semantic embeddings with validation and caching."""
        cache_dir = Path("cache")
        cache_dir.mkdir(exist_ok=True)

        cache_key_data = {
            "model": SEMANTIC_MODEL_NAME,
            "product_count": len(self.products),
            "product_ids": [p.get("id") for p in self.products],
        }
        cache_key = hashlib.md5(json.dumps(cache_key_data, sort_keys=True).encode()).hexdigest()

        embeddings_file = cache_dir / f"embeddings_{cache_key}.npy"
        metadata_file = cache_dir / f"metadata_{cache_key}.json"

        if embeddings_file.exists() and metadata_file.exists():
            print("Loading cached embeddings...")
            self.product_embeddings = np.load(embeddings_file)
            self.semantic_model = SentenceTransformer(SEMANTIC_MODEL_NAME)
            return

        self.semantic_model = SentenceTransformer(SEMANTIC_MODEL_NAME)

        product_texts = []
        for p in self.products:
            text = f"{p.get('name', '')} {p.get('description', '')}"
            product_texts.append(text)

        self.product_embeddings = self.semantic_model.encode(
            product_texts,
            batch_size=EMBEDDING_BATCH_SIZE,
            show_progress_bar=True,
            convert_to_numpy=True,
        )

        # Save to cache for next time
        print("Saving embeddings to cache...")
        np.save(embeddings_file, self.product_embeddings)
        with open(metadata_file, "w") as f:
            json.dump(cache_key_data, f, indent=2)
        print(f"Cache key: {cache_key}")

    def _get_bm25_scores(self, query: str) -> np.ndarray:
        query_tokens = _normalize(query)

        name_scores = self.bm25_name.get_scores(query_tokens)
        description_scores = self.bm25_description.get_scores(query_tokens)
        brand_scores = self.bm25_brand.get_scores(query_tokens)

        bm25_scores = (
            name_scores * self.name_boost
            + description_scores * self.description_boost
            + brand_scores * self.brand_boost
        )

        max_score = bm25_scores.max()
        if max_score > 0:
            bm25_scores = bm25_scores / max_score

        return bm25_scores

    def _get_semantic_scores(self, query: str) -> np.ndarray:
        query_embedding = self.semantic_model.encode([query], convert_to_numpy=True)
        semantic_scores = cosine_similarity(query_embedding, self.product_embeddings)[0]

        semantic_scores = (semantic_scores + 1) / 2

        return semantic_scores

    def search(self, query: str, limit: int = 10) -> list[tuple[float, dict[str, Any]]]:
        """
        Hybrid search combining BM25 and semantic similarity.
        Returns empty list if best match is below quality threshold.
        """
        bm25_scores = self._get_bm25_scores(query)
        semantic_scores = self._get_semantic_scores(query)

        hybrid_scores = (
            LEXICAL_WEIGHT * bm25_scores + SEMANTIC_WEIGHT * semantic_scores
        )

        top_score = hybrid_scores.max()
        if top_score < MIN_TOP_SCORE:
            return []

        scored = []
        for i, product in enumerate(self.products):
            scored.append((float(hybrid_scores[i]), product))

        scored.sort(key=lambda x: (-x[0], x[1].get("id", 0)))

        return scored[:limit]
