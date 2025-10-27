#!/usr/bin/env python3
"""Wikipedia extractor - extracts URLs from wikiextractor JSON output."""

import json
from pathlib import Path


def extract_wikipedia_urls(input_dir, output_file='wikipedia_urls.txt', max_urls=None):
    """Extract deduplicated URLs from wikiextractor JSON output.

    Expects input from: python -m wikiextractor.WikiExtractor dump.xml.bz2 --json -o input_dir/
    Output: Text file with one URL per line (deduplicated)
    """
    print(f"Processing wikiextractor output: {input_dir}")
    print(f"Max URLs: {max_urls if max_urls else 'unlimited'}")

    seen_urls = set()
    url_count = 0

    # Find all wiki_* files recursively
    wiki_files = sorted(Path(input_dir).rglob('wiki_*'))

    with open(output_file, 'w', encoding='utf-8') as out:
        for wiki_file in wiki_files:
            with open(wiki_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        doc = json.loads(line)
                        url = doc.get('url', '')

                        if url and url not in seen_urls:
                            out.write(f"{url}\n")
                            seen_urls.add(url)
                            url_count += 1

                            if url_count % 1000 == 0:
                                print(f"Extracted {url_count} URLs...")

                            if max_urls and url_count >= max_urls:
                                print(f"\nExtracted {url_count} unique URLs to {output_file}")
                                return url_count

                    except json.JSONDecodeError:
                        continue

    print(f"\nExtracted {url_count} unique URLs to {output_file}")
    print(f"\nNext step: textnano urls {output_file} output_dir/")
    return url_count
