#!/usr/bin/env python3
"""Reddit extractor - merges pre-extracted Reddit URL files."""

from pathlib import Path


def extract_reddit_urls(input_dir, output_file='reddit_urls.txt', max_urls=None):
    """Merge Reddit URL files into single deduplicated list.

    Expects: Directory with RS_*.bz2.deduped.txt files
    Download from: https://drive.google.com/file/d/1hRtA3zZ0K5UHKOQ0_8d0BIc_1VyxgY51/view
    Each file contains one URL per line (already deduplicated per file)
    """
    print(f"Processing Reddit URL files: {input_dir}")
    print(f"Max URLs: {max_urls if max_urls else 'unlimited'}")

    seen_urls = set()
    url_count = 0

    # Find all RS_*.txt files
    url_files = sorted(Path(input_dir).glob('RS_*.txt'))

    if not url_files:
        print(f"No RS_*.txt files found in {input_dir}")
        return 0

    with open(output_file, 'w', encoding='utf-8') as out:
        for url_file in url_files:
            print(f"Processing {url_file.name}...")

            with open(url_file, 'r', encoding='utf-8') as f:
                for line in f:
                    url = line.strip()
                    if not url or url in seen_urls:
                        continue

                    out.write(f"{url}\n")
                    seen_urls.add(url)
                    url_count += 1

                    if url_count % 10000 == 0:
                        print(f"  Merged {url_count} URLs...")

                    if max_urls and url_count >= max_urls:
                        print(f"\nExtracted {url_count} unique URLs to {output_file}")
                        print(f"\nNext step: textnano urls {output_file} output_dir/")
                        return url_count

    print(f"\nExtracted {url_count} unique URLs to {output_file}")
    print(f"\nNext step: textnano urls {output_file} output_dir/")
    return url_count
