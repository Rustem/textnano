#!/usr/bin/env python3
"""Gutenberg extractor - generates URLs from book IDs."""

import urllib.request


def exists(url):
    """Check if URL exists."""
    try:
        req = urllib.request.Request(url, method='HEAD')
        urllib.request.urlopen(req, timeout=5)
        return True
    except:
        return False


def get_gutenberg_link_from_id(book_id):
    """Find valid Gutenberg URL for a book ID."""
    txt_tmpl1 = 'http://www.gutenberg.org/cache/epub/{}/pg{}.txt'
    txt_tmpl2 = 'http://www.gutenberg.org/files/{}/{}.txt'

    for tmpl in [txt_tmpl1, txt_tmpl2]:
        link = tmpl.format(book_id, book_id)
        if exists(link):
            return link

    txt_tmpl3 = 'http://www.gutenberg.org/files/{}/{}-{}.txt'
    for i in [0, 8]:
        link = txt_tmpl3.format(book_id, book_id, i)
        if exists(link):
            return link

    return None


def extract_gutenberg_urls(output_file='gutenberg_urls.txt', max_id=58910):
    """Generate Gutenberg URLs by checking book IDs.

    Args:
        output_file: Output URL list file
        max_id: Maximum book ID to check (default: 58910)
    """
    print(f"Generating Gutenberg URLs for book IDs 1-{max_id}")
    print("This may take a while as it checks each URL...")

    url_count = 0

    with open(output_file, 'w', encoding='utf-8') as out:
        for book_id in range(1, max_id + 1):
            link = get_gutenberg_link_from_id(book_id)

            if link:
                out.write(f"{link}\n")
                url_count += 1

                if url_count % 100 == 0:
                    print(f"Found {url_count} books...")
            else:
                print(f"Can't find link for book id {book_id}")

    print(f"\nGenerated {url_count} URLs to {output_file}")
    print(f"\nNext step: textnano urls {output_file} output_dir/")
    return url_count
