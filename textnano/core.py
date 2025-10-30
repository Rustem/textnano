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
from pathlib import Path
from typing import Optional, Set, Dict, List
from urllib.parse import urlparse

from .config import DEFAULT_EXCLUDE_DOMAINS, DEFAULT_EXCLUDE_EXTENSIONS
from .utils import print_stats, estimate_dataset_size, merge_datasets


# =============================================================================
# DOWNLOAD
# =============================================================================

def download_text(url: str, timeout: int = 30) -> Optional[str]:
    """Download and extract text from a URL.

    Returns:
        str or None: Cleaned text content, or None if failed
    """
    try:
        # Download
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)

        # Create SSL context that doesn't verify certificates
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(req, timeout=timeout, context=context) as response:
            content = response.read().decode('utf-8', errors='ignore')

        # Basic HTML cleaning
        text = clean_html(content)

        return text if text.strip() else None

    except Exception:
        return None


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
    # Unescape HTML entities
    text = html.unescape(html_content)

    # Remove script and style tags
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)

    # Remove leading/trailing whitespace
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
    words = text.lower().split()[:n]
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
    print(f"Processing {len(urls)} URLs...")

    with open(os.path.join(output_dir, 'success.txt'), 'w') as success_log, \
         open(os.path.join(output_dir, 'failed.txt'), 'w') as failed_log:

        for idx, url in enumerate(urls, 1):
            print(f"[{idx}/{len(urls)}] {url[:60]}...")

            # Check exclusion filters
            parsed = urlparse(url)

            # Check domain exclusion
            if exclude_domains and any(domain in parsed.netloc for domain in exclude_domains):
                failed_log.write(f"{url}\texcluded_domain\n")
                stats['excluded'] += 1
                print("  ⊘ Excluded domain")
                continue

            # Check extension exclusion
            if exclude_extensions:
                path_lower = parsed.path.lower()
                if any(path_lower.endswith(f'.{ext}') for ext in exclude_extensions):
                    failed_log.write(f"{url}\texcluded_extension\n")
                    stats['excluded'] += 1
                    print("  ⊘ Excluded extension")
                    continue

            # Download
            text = download_text(url)

            if not text:
                failed_log.write(f"{url}\n")
                stats['failed'] += 1
                print("  ✗ Failed to download")
                continue

            # Check length
            word_count = len(text.split())
            if word_count < min_words:
                failed_log.write(f"{url}\ttoo_short:{word_count}\n")
                stats['too_short'] += 1
                print(f"  ⊘ Too short ({word_count} words)")
                continue

            # Check duplicate
            if is_duplicate(text, seen_fingerprints):
                stats['duplicates'] += 1
                print("  ⊘ Duplicate")
                continue

            # Save
            output_file = os.path.join(output_dir, f"{stats['success']+1:04d}.txt")
            with open(output_file, 'w') as f:
                f.write(f"{url}\n\n")  # First line = URL
                f.write(text)

            success_log.write(f"{url}\n")
            stats['success'] += 1
            print(f"  ✓ Saved ({word_count} words)")

    # Print summary
    print_stats(stats)

    return stats


# =============================================================================
# CLI
# =============================================================================

def main():
    """Command-line interface."""
    import sys
    import argparse

    # Check for simple commands (backward compatibility)
    if len(sys.argv) >= 2 and sys.argv[1] == 'stats':
        if len(sys.argv) < 3:
            print("Usage: textnano stats <dir>")
            sys.exit(1)
        stats = estimate_dataset_size(sys.argv[2])
        print(f"Files:     {stats['files']}")
        print(f"Words:     {stats['words']:,}")
        print(f"Size:      {stats['mb']:.1f} MB")
        print(f"Avg/file:  {stats['avg_words_per_file']} words")
        return

    if len(sys.argv) >= 2 and sys.argv[1] == 'merge':
        if len(sys.argv) < 4:
            print("Usage: textnano merge <dir1> <dir2> ... <output_dir>")
            sys.exit(1)
        output = sys.argv[-1]
        inputs = sys.argv[2:-1]
        merge_datasets(*inputs, output_dir=output, is_duplicate_func=is_duplicate)
        return

    # Parse arguments
    parser = argparse.ArgumentParser(
        description='textnano - Minimal text dataset builder',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('url_file', help='File with URLs (one per line)')
    parser.add_argument('output_dir', help='Output directory')
    parser.add_argument('max_urls', nargs='?', type=int, default=None,
                        help='Maximum URLs to process')
    parser.add_argument('--exclude-domains', '-ed', nargs='+',
                        help='Additional domains to exclude (adds to defaults)')
    parser.add_argument('--exclude-extensions', '-ee', nargs='+',
                        help='Additional file extensions to exclude (adds to defaults)')
    parser.add_argument('--no-default-excludes', action='store_true',
                        help='Disable default exclusion lists (only use custom excludes)')

    args = parser.parse_args()

    # Download command
    stats = download_and_clean(
        args.url_file,
        args.output_dir,
        max_urls=args.max_urls,
        exclude_domains=args.exclude_domains,
        exclude_extensions=args.exclude_extensions,
        use_default_excludes=not args.no_default_excludes
    )

    # Show dataset stats
    dataset_stats = estimate_dataset_size(args.output_dir)
    print(f"\nDataset: {dataset_stats['files']} files, "
          f"{dataset_stats['words']:,} words, "
          f"{dataset_stats['mb']:.1f} MB")


if __name__ == '__main__':
    main()


# =============================================================================
# USAGE EXAMPLES (copy these to test)
# =============================================================================

"""
# Example 1: Basic usage
python textnano.py urls.txt dataset/

# Example 2: Limit to 100 URLs
python textnano.py urls.txt dataset/ 100

# Example 3: In Python
import textnano

textnano.download_and_clean('urls.txt', 'output/')
stats = textnano.estimate_dataset_size('output/')
print(f"Got {stats['words']:,} words")

# Example 4: Create sample URLs file
cat > urls.txt << EOF
https://en.wikipedia.org/wiki/Machine_learning
https://en.wikipedia.org/wiki/Deep_learning
https://en.wikipedia.org/wiki/Natural_language_processing
https://en.wikipedia.org/wiki/Computer_vision
https://www.gutenberg.org/files/1342/1342-h/1342-h.htm
EOF

# Example 5: Get stats
python textnano.py stats dataset/

# Example 6: Merge datasets
python textnano.py merge dataset1/ dataset2/ merged/
"""
