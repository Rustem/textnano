"""
textnano - Minimal text dataset builder (nano lazynlp)

A single-file library to build text datasets from web URLs.
Perfect for ML students who just want clean text quickly.

Dependencies: httpx, protego (for async parallel crawling with robots.txt support)
"""

from textnano.core import (
    download_text,
    download_text_async,
    clean_html,
    text_fingerprint,
    is_duplicate,
    download_and_clean,
    download_and_clean_async,
    estimate_dataset_size,
    merge_datasets,
)

__version__ = "0.2.0"
__all__ = [
    "download_text",
    "download_text_async",
    "clean_html",
    "text_fingerprint",
    "is_duplicate",
    "download_and_clean",
    "download_and_clean_async",
    "estimate_dataset_size",
    "merge_datasets",
]
