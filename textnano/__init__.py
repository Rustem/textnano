"""
textnano - Minimal text dataset builder (nano lazynlp)

A single-file library to build text datasets from web URLs.
Perfect for ML students who just want clean text quickly.

Dependencies: ZERO (pure Python stdlib)
"""

from textnano.core import (
    download_text,
    clean_html,
    text_fingerprint,
    is_duplicate,
    download_and_clean,
    estimate_dataset_size,
    merge_datasets,
)

__version__ = "0.1.0"
__all__ = [
    "download_text",
    "clean_html",
    "text_fingerprint",
    "is_duplicate",
    "download_and_clean",
    "estimate_dataset_size",
    "merge_datasets",
]
