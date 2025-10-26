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
from pathlib import Path


# =============================================================================
# DOWNLOAD
# =============================================================================

def download_text(url, timeout=30):
    """Download and extract text from a URL.

    Returns:
        str or None: Cleaned text content, or None if failed
    """
    try:
        # Download
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content = response.read().decode('utf-8', errors='ignore')

        # Basic HTML cleaning
        text = clean_html(content)

        return text if text.strip() else None

    except Exception:
        return None


# =============================================================================
# CLEANING
# =============================================================================

def clean_html(html_content):
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

def text_fingerprint(text, n=8):
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


def is_duplicate(text, seen_fingerprints, threshold=0.8):
    """Check if text is duplicate based on fingerprint.

    Args:
        text: Text to check
        seen_fingerprints: Set of seen fingerprints
        threshold: Not used in this simple version

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

def download_and_clean(url_file, output_dir, min_words=50, max_urls=None):
    """Download text from URLs, clean, and deduplicate.

    Args:
        url_file: Path to file with one URL per line
        output_dir: Directory to save text files
        min_words: Minimum words per document (default: 50)
        max_urls: Maximum URLs to process (default: None = all)

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

    # Read URLs
    with open(url_file) as f:
        urls = [line.strip() for line in f if line.strip()]

    if max_urls:
        urls = urls[:max_urls]

    # Open log files
    success_log = open(os.path.join(output_dir, 'success.txt'), 'w')
    failed_log = open(os.path.join(output_dir, 'failed.txt'), 'w')

    # Deduplication
    seen_fingerprints = set()

    # Counters
    stats = {'success': 0, 'failed': 0, 'duplicates': 0, 'too_short': 0}

    # Process each URL
    print(f"Processing {len(urls)} URLs...")

    for idx, url in enumerate(urls, 1):
        print(f"[{idx}/{len(urls)}] {url[:60]}...")

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

    # Cleanup
    success_log.close()
    failed_log.close()

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Success:    {stats['success']:4d}")
    print(f"Failed:     {stats['failed']:4d}")
    print(f"Too short:  {stats['too_short']:4d}")
    print(f"Duplicates: {stats['duplicates']:4d}")
    print(f"Total:      {len(urls):4d}")
    print("="*60)

    return stats


# =============================================================================
# UTILITIES
# =============================================================================

def estimate_dataset_size(output_dir):
    """Get statistics about the dataset.

    Args:
        output_dir: Directory containing .txt files

    Returns:
        dict: Statistics
    """
    txt_files = list(Path(output_dir).glob('*.txt'))
    txt_files = [f for f in txt_files if f.stem.isdigit()]

    total_words = 0
    total_chars = 0

    for file in txt_files:
        with open(file) as f:
            content = f.read()
            total_words += len(content.split())
            total_chars += len(content)

    return {
        'files': len(txt_files),
        'words': total_words,
        'chars': total_chars,
        'mb': total_chars / (1024 * 1024),
        'avg_words_per_file': total_words // len(txt_files) if txt_files else 0
    }


def merge_datasets(*dirs, output_dir):
    """Merge multiple datasets and deduplicate.

    Args:
        *dirs: Input directories
        output_dir: Output directory
    """
    os.makedirs(output_dir, exist_ok=True)

    seen_fingerprints = set()
    output_idx = 1

    for input_dir in dirs:
        txt_files = sorted(Path(input_dir).glob('[0-9]*.txt'))

        for file in txt_files:
            with open(file) as f:
                content = f.read()

            # Skip duplicates
            if is_duplicate(content, seen_fingerprints):
                continue

            # Copy to output
            output_file = os.path.join(output_dir, f"{output_idx:04d}.txt")
            with open(output_file, 'w') as f:
                f.write(content)

            output_idx += 1

    print(f"Merged {output_idx-1} unique documents from {len(dirs)} datasets")


# =============================================================================
# CLI
# =============================================================================

def main():
    """Command-line interface."""
    import sys

    if len(sys.argv) < 3:
        print(__doc__)
        print("\nUsage:")
        print("  python textnano.py <url_file> <output_dir> [max_urls]")
        print("\nExamples:")
        print("  python textnano.py urls.txt dataset/")
        print("  python textnano.py urls.txt dataset/ 100")
        print("\nCommands:")
        print("  stats <dir>              Show dataset statistics")
        print("  merge <dir1> <dir2> ...  Merge multiple datasets")
        sys.exit(1)

    command = sys.argv[1]

    # Stats command
    if command == 'stats':
        stats = estimate_dataset_size(sys.argv[2])
        print(f"Files:     {stats['files']}")
        print(f"Words:     {stats['words']:,}")
        print(f"Size:      {stats['mb']:.1f} MB")
        print(f"Avg/file:  {stats['avg_words_per_file']} words")
        return

    # Merge command
    if command == 'merge':
        output = sys.argv[-1]
        inputs = sys.argv[2:-1]
        merge_datasets(*inputs, output_dir=output)
        return

    # Download command
    url_file = sys.argv[1]
    output_dir = sys.argv[2]
    max_urls = int(sys.argv[3]) if len(sys.argv) > 3 else None

    stats = download_and_clean(url_file, output_dir, max_urls=max_urls)

    # Show dataset stats
    dataset_stats = estimate_dataset_size(output_dir)
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
