#!/usr/bin/env python3
"""
textnano.py - Minimal text dataset builder (nano lazynlp)

A single-file library to build text datasets from web URLs.
Perfect for ML students who just want clean text quickly.

Usage:
    python textnano.py urls.txt output/

Or in code:
    import textnano
    textnano.download_and_clean('urls.txt', 'output/')

Dependencies: ZERO (pure Python stdlib)
Lines of code: ~200
"""

import os
import re
import html
import urllib.request
import hashlib
import ssl
import logging
from pathlib import Path
from typing import Optional, Set, Dict, List
from urllib.parse import urlparse

from .config import DEFAULT_EXCLUDE_DOMAINS, DEFAULT_EXCLUDE_EXTENSIONS
from .utils import print_stats, estimate_dataset_size, merge_datasets

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')


# =============================================================================
# DOWNLOAD
# =============================================================================

def download_text(url: str, timeout: int = 30) -> str:
    """Download and extract text from a URL.

    Returns:
        str: Cleaned text content, or empty string if failed
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(req, timeout=timeout, context=context) as response:
            content = response.read().decode('utf-8', errors='ignore')

        return clean_html(content)

    except urllib.error.HTTPError as e:
        logging.error(f"HTTP error {e.code} for {url}: {e.reason}")
        return ""
    except urllib.error.URLError as e:
        logging.error(f"URL error for {url}: {e.reason}")
        return ""
    except Exception as e:
        logging.error(f"Unexpected error for {url}: {type(e).__name__}: {e}")
        return ""


# =============================================================================
# CLEANING
# =============================================================================

def clean_html(html_content: str) -> str:
    """Remove HTML tags and clean text.

    Args:
        html_content: Raw HTML string

    Returns:
        str: Clean text
    """
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = text.strip()

    return text


# =============================================================================
# DEDUPLICATION
# =============================================================================

def text_fingerprint(text: str, n: int = 8) -> str:
    """Create fingerprint of text using first N words.

    Args:
        text: Input text
        n: Number of words to use (default: 8)

    Returns:
        str: MD5 hash of first N words
    """
    words = text.lower().split(maxsplit=n)[:n]
    fingerprint_text = ' '.join(words)
    return hashlib.md5(fingerprint_text.encode()).hexdigest()


def is_duplicate(text: str, seen_fingerprints: Set[str]) -> bool:
    """Check if text is duplicate based on fingerprint.

    Args:
        text: Text to check
        seen_fingerprints: Set of seen fingerprints

    Returns:
        bool: True if duplicate
    """
    fp = text_fingerprint(text)

    if fp in seen_fingerprints:
        return True

    seen_fingerprints.add(fp)
    return False


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def download_and_clean(url_file: str, output_dir: str, min_words: int = 50, max_urls: Optional[int] = None,
                       exclude_domains: Optional[List[str]] = None, exclude_extensions: Optional[List[str]] = None,
                       use_default_excludes: bool = True) -> Dict[str, int]:
    """Download text from URLs, clean, and deduplicate.

    Args:
        url_file: Path to file with one URL per line
        output_dir: Directory to save text files
        min_words: Minimum words per document (default: 50)
        max_urls: Maximum URLs to process (default: None = all)
        exclude_domains: List of domains to exclude (default: None, uses defaults if use_default_excludes=True)
        exclude_extensions: List of file extensions to exclude (default: None, uses defaults if use_default_excludes=True)
        use_default_excludes: Use default exclusion lists (default: True)

    Output structure:
        output_dir/
        ├── 0001.txt          # Text files
        ├── 0002.txt
        ├── success.txt       # Successfully processed URLs
        └── failed.txt        # Failed URLs

    Returns:
        dict: Statistics {success: int, failed: int, duplicates: int}
    """
    # Setup
    os.makedirs(output_dir, exist_ok=True)

    # Normalize filters
    if use_default_excludes:
        exclude_domains = set(exclude_domains or []) | set(DEFAULT_EXCLUDE_DOMAINS)
        exclude_extensions = set(ext.lower().lstrip('.') for ext in (exclude_extensions or [])) | set(DEFAULT_EXCLUDE_EXTENSIONS)
    else:
        exclude_domains = set(exclude_domains or [])
        exclude_extensions = set(ext.lower().lstrip('.') for ext in (exclude_extensions or []))

    # Read URLs
    with open(url_file) as f:
        urls = [line.strip() for line in f if line.strip()]

    if max_urls:
        urls = urls[:max_urls]

    # Deduplication
    seen_fingerprints = set()

    # Counters
    stats = {'success': 0, 'failed': 0, 'duplicates': 0, 'too_short': 0, 'excluded': 0}

    # Process each URL
    logging.info(f"Processing {len(urls)} URLs...")

    with open(os.path.join(output_dir, 'success.txt'), 'w') as success_log, \
         open(os.path.join(output_dir, 'failed.txt'), 'w') as failed_log:

        for idx, url in enumerate(urls, 1):
            logging.info(f"[{idx}/{len(urls)}] {url[:60]}...")

            # Check exclusion filters
            parsed = urlparse(url)

            # Check domain exclusion
            if exclude_domains and any(domain in parsed.netloc for domain in exclude_domains):
                failed_log.write(f"{url}\texcluded_domain\n")
                stats['excluded'] += 1
                logging.info("  ⊘ Excluded domain")
                continue

            # Check extension exclusion
            if exclude_extensions:
                path_lower = parsed.path.lower()
                if any(path_lower.endswith(f'.{ext}') for ext in exclude_extensions):
                    failed_log.write(f"{url}\texcluded_extension\n")
                    stats['excluded'] += 1
                    logging.info("  ⊘ Excluded extension")
                    continue

            # Download
            text = download_text(url)

            if not text:
                failed_log.write(f"{url}\n")
                stats['failed'] += 1
                logging.warning("  ✗ Failed to download")
                continue

            # Check length
            word_count = len(text.split())
            if word_count < min_words:
                failed_log.write(f"{url}\ttoo_short:{word_count}\n")
                stats['too_short'] += 1
                logging.info(f"  ⊘ Too short ({word_count} words)")
                continue

            # Check duplicate
            if is_duplicate(text, seen_fingerprints):
                stats['duplicates'] += 1
                logging.info("  ⊘ Duplicate")
                continue

            # Save
            output_file = os.path.join(output_dir, f"{stats['success']+1:04d}.txt")
            with open(output_file, 'w') as f:
                f.write(f"{url}\n\n")  # First line = URL
                f.write(text)

            success_log.write(f"{url}\n")
            stats['success'] += 1
            logging.info(f"  ✓ Saved ({word_count} words)")

    # Print summary
    print_stats(stats)

    return stats
