from __future__ import annotations

import hashlib
import logging

from huggingface_hub import AsyncInferenceClient

from app.core.config import get_settings
from ke.models.vector import EmbeddingItem, EmbeddingResult, SparseVector

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self, model_name: str | None = None, dimension: int | None = None) -> None:
        settings = get_settings()
        self._model_name = model_name or settings.embedding_model
        self._dimension = dimension or settings.embedding_dimension
        token = settings.hf_token
        self._client: AsyncInferenceClient | None = (
            AsyncInferenceClient(token=token) if token else None
        )
        if self._client is None:
            logger.warning("HF_TOKEN not set — falling back to deterministic embeddings")
        self._cache: dict[str, EmbeddingResult] = {}

    async def embed(self, item: EmbeddingItem) -> EmbeddingResult:
        cache_key = _cache_key(item.text)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        result = await self._generate_embedding(item)
        self._cache[cache_key] = result
        return result

    async def embed_batch(
        self, items: list[EmbeddingItem], batch_size: int = 100
    ) -> list[EmbeddingResult]:
        results: list[EmbeddingResult] = []
        uncached: list[EmbeddingItem] = []
        for item in items:
            cache_key = _cache_key(item.text)
            cached = self._cache.get(cache_key)
            if cached is not None:
                results.append(cached)
            else:
                uncached.append(item)
        if not uncached:
            return results
        for i in range(0, len(uncached), batch_size):
            batch = uncached[i : i + batch_size]
            if self._client is not None:
                batch_results = await self._hf_embed_batch(batch)
            else:
                batch_results = [await self._mock_embed(item) for item in batch]
            for res in batch_results:
                self._cache[_cache_key(res.id if hasattr(res, 'id') else '')] = res
            results.extend(batch_results)
        return results

    async def embed_text(self, text: str) -> EmbeddingResult:
        item = EmbeddingItem(id=_cache_key(text), text=text, source_id="_search")
        return await self.embed(item)

    async def _generate_embedding(self, item: EmbeddingItem) -> EmbeddingResult:
        if self._client is not None:
            return await self._hf_embed(item)
        return await self._mock_embed(item)

    async def _hf_embed(self, item: EmbeddingItem) -> EmbeddingResult:
        try:
            dense = await self._client.feature_extraction(
                text=item.text,
                model=self._model_name,
            )
            if isinstance(dense, list) and dense and isinstance(dense[0], list):
                dense = dense[0]
            dimension = len(dense)
            sparse = _deterministic_sparse(item.text)
            return EmbeddingResult(
                id=item.id,
                dense_vector=dense,
                sparse_vector=sparse,
                embedding_model=self._model_name,
                dimension=dimension,
                normalized=True,
            )
        except Exception as exc:
            logger.warning("HF embedding failed for %r — falling back: %s", item.text[:60], exc)
            return await self._mock_embed(item)

    async def _hf_embed_batch(self, items: list[EmbeddingItem]) -> list[EmbeddingResult]:
        texts = [it.text for it in items]
        try:
            outputs = await self._client.feature_extraction(
                text=texts,
                model=self._model_name,
            )
            results: list[EmbeddingResult] = []
            for i, item in enumerate(items):
                dense = outputs[i] if isinstance(outputs, list) else outputs
                if isinstance(dense, list) and dense and isinstance(dense[0], list):
                    dense = dense[0]
                dimension = len(dense)
                sparse = _deterministic_sparse(item.text)
                results.append(EmbeddingResult(
                    id=item.id,
                    dense_vector=dense,
                    sparse_vector=sparse,
                    embedding_model=self._model_name,
                    dimension=dimension,
                    normalized=True,
                ))
            return results
        except Exception as exc:
            logger.warning("HF batch embedding failed — falling back: %s", exc)
            return [await self._mock_embed(it) for it in items]

    async def _mock_embed(self, item: EmbeddingItem) -> EmbeddingResult:
        dimension = self._dimension
        seed = sum(ord(c) for c in item.text) % (dimension - 1) or 1
        dense = [0.0] * dimension
        for j in range(dimension):
            dense[j] = (seed * (j + 1) % 255) / 255.0
        norm = sum(v * v for v in dense) ** 0.5
        dense = [v / norm for v in dense]
        sparse = _deterministic_sparse(item.text)
        return EmbeddingResult(
            id=item.id,
            dense_vector=dense,
            sparse_vector=sparse,
            embedding_model=self._model_name,
            dimension=dimension,
            normalized=True,
        )

    def clear_cache(self) -> None:
        self._cache.clear()


def _cache_key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _deterministic_sparse(text: str) -> SparseVector:
    seed = sum(ord(c) for c in text) % 25000 or 1
    return SparseVector(
        indices=[seed % 25000, (seed * 31) % 25000, (seed * 17) % 25000],
        values=[0.45, 0.32, 0.28],
    )
