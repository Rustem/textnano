#!/usr/bin/env python3
"""CLI for textnano with extractor subcommands."""

import sys
import asyncio
import argparse
from textnano.core import download_and_clean_async, is_duplicate
from textnano.utils import estimate_dataset_size, merge_datasets
from textnano.extractors import extract_wikipedia_urls, extract_reddit_urls, extract_gutenberg_urls


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='textnano - Minimal text dataset builder',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # urls command (main functionality)
    urls_parser = subparsers.add_parser('urls', help='Download and clean from URL list')
    urls_parser.add_argument('url_file', help='File with URLs (one per line)')
    urls_parser.add_argument('output_dir', help='Output directory')
    urls_parser.add_argument('max_urls', nargs='?', type=int, default=None,
                            help='Maximum URLs to process')
    urls_parser.add_argument('--exclude-domains', '-ed', nargs='+',
                            help='Additional domains to exclude')
    urls_parser.add_argument('--exclude-extensions', '-ee', nargs='+',
                            help='Additional file extensions to exclude')
    urls_parser.add_argument('--no-default-excludes', action='store_true',
                            help='Disable default exclusion lists')
    urls_parser.add_argument('--max-concurrent', '-c', type=int, default=10,
                            help='Maximum concurrent requests (default: 10)')
    urls_parser.add_argument('--no-robots', action='store_true',
                            help='Ignore robots.txt (not recommended)')
    urls_parser.add_argument('--timeout', '-t', type=int, default=30,
                            help='Request timeout in seconds (default: 30)')

    # wikipedia command
    wiki_parser = subparsers.add_parser('wikipedia', help='Extract URLs from Wikipedia dump')
    wiki_parser.add_argument('input_dir', help='Directory with wikiextractor JSON output')
    wiki_parser.add_argument('--output', '-o', default='wikipedia_urls.txt',
                            help='Output URL file (default: wikipedia_urls.txt)')
    wiki_parser.add_argument('--max', type=int, default=None,
                            help='Maximum URLs to extract')

    # reddit command
    reddit_parser = subparsers.add_parser('reddit', help='Merge Reddit URL files')
    reddit_parser.add_argument('input_dir', help='Directory with RS_*.txt files')
    reddit_parser.add_argument('--output', '-o', default='reddit_urls.txt',
                             help='Output URL file (default: reddit_urls.txt)')
    reddit_parser.add_argument('--max', type=int, default=None,
                             help='Maximum URLs to extract')

    # gutenberg command
    gutenberg_parser = subparsers.add_parser('gutenberg', help='Generate Gutenberg URLs')
    gutenberg_parser.add_argument('--output', '-o', default='gutenberg_urls.txt',
                                 help='Output URL file (default: gutenberg_urls.txt)')
    gutenberg_parser.add_argument('--max-id', type=int, default=58910,
                                 help='Maximum book ID (default: 58910)')

    # stats command
    stats_parser = subparsers.add_parser('stats', help='Show dataset statistics')
    stats_parser.add_argument('dir', help='Dataset directory')

    # merge command
    merge_parser = subparsers.add_parser('merge', help='Merge multiple datasets')
    merge_parser.add_argument('dirs', nargs='+', help='Input directories and output dir (last one)')

    args = parser.parse_args()

    # Handle commands
    if args.command == 'urls':
        stats = asyncio.run(download_and_clean_async(
            args.url_file,
            args.output_dir,
            max_urls=args.max_urls,
            exclude_domains=args.exclude_domains,
            exclude_extensions=args.exclude_extensions,
            use_default_excludes=not args.no_default_excludes,
            max_concurrent=args.max_concurrent,
            respect_robots=not args.no_robots,
            timeout=args.timeout
        ))
        dataset_stats = estimate_dataset_size(args.output_dir)
        print(f"\nDataset: {dataset_stats['files']} files, "
              f"{dataset_stats['words']:,} words, "
              f"{dataset_stats['mb']:.1f} MB")

    elif args.command == 'wikipedia':
        extract_wikipedia_urls(args.input_dir, args.output, args.max)

    elif args.command == 'reddit':
        extract_reddit_urls(args.input_dir, args.output, args.max)

    elif args.command == 'gutenberg':
        extract_gutenberg_urls(args.output, args.max_id)

    elif args.command == 'stats':
        stats = estimate_dataset_size(args.dir)
        print(f"Files:     {stats['files']}")
        print(f"Words:     {stats['words']:,}")
        print(f"Size:      {stats['mb']:.1f} MB")
        print(f"Avg/file:  {stats['avg_words_per_file']} words")

    elif args.command == 'merge':
        output = args.dirs[-1]
        inputs = args.dirs[:-1]
        merge_datasets(*inputs, output_dir=output, is_duplicate_func=is_duplicate)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
