"""
Extractors for different data sources.

All extractors generate URL lists that can be used with textnano core:
- Extract URLs from source-specific dumps
- Output: text file with one URL per line
- Then use: textnano urls <url_file> <output_dir>
"""

from textnano.extractors.wikipedia import extract_wikipedia_urls
from textnano.extractors.reddit import extract_reddit_urls
from textnano.extractors.gutenberg import extract_gutenberg_urls

__all__ = [
    "extract_wikipedia_urls",
    "extract_reddit_urls",
    "extract_gutenberg_urls",
]
