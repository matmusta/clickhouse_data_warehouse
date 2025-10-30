from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Iterable, List, Optional

from sentence_transformers import SentenceTransformer

from .config import AppConfig, load_config


def model_directory(model_name: str, paths_root: Path) -> Path:
    safe_name = model_name.replace("/", "__")
    return paths_root / safe_name


@lru_cache(maxsize=2)
def load_embedding_model(*, model_name: Optional[str] = None, config: Optional[AppConfig] = None) -> SentenceTransformer:
    cfg = config or load_config()
    target = model_name or cfg.models.active
    model_path = model_directory(target, cfg.paths.model_cache_dir)

    if not model_path.exists():
        raise FileNotFoundError(
            f"Embedding model '{target}' not found at {model_path}. "
            "Run python/scripts/download_models.py to populate the cache."
        )

    return SentenceTransformer(str(model_path))


def embed_texts(texts: Iterable[str], *, model_name: Optional[str] = None, config: Optional[AppConfig] = None) -> List[List[float]]:
    model = load_embedding_model(model_name=model_name, config=config)
    embeddings = model.encode(
        list(texts), convert_to_numpy=True, convert_to_tensor=False, normalize_embeddings=False
    )
    return [[float(value) for value in vector] for vector in embeddings.tolist()]


def embedding_dimension(*, model_name: Optional[str] = None, config: Optional[AppConfig] = None) -> int:
    model = load_embedding_model(model_name=model_name, config=config)
    return int(model.get_sentence_embedding_dimension())
