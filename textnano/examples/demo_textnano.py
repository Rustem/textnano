#!/usr/bin/env python3
"""
demo_textnano.py - Quick demonstration of textnano

Run this to see textnano in action with sample data.
"""

import textnano
import os


def demo_basic():
    """Demo 1: Basic usage with sample URLs."""
    print("="*70)
    print("DEMO 1: Basic Usage")
    print("="*70)
    print()

    # Create a small test URL file
    test_urls = """
https://en.wikipedia.org/wiki/Machine_learning
https://en.wikipedia.org/wiki/Deep_learning
https://en.wikipedia.org/wiki/Artificial_neural_network
""".strip()

    with open('demo_urls.txt', 'w') as f:
        f.write(test_urls)

    print("Created demo_urls.txt with 3 Wikipedia articles")
    print()

    # Download and clean
    print("Downloading and cleaning...")
    print()

    stats = textnano.download_and_clean(
        url_file='demo_urls.txt',
        output_dir='demo_dataset/',
        min_words=50
    )

    print()
    print(f"✓ Success: {stats['success']} documents")
    print(f"✗ Failed:  {stats['failed']} documents")
    print()

    # Show dataset stats
    dataset_stats = textnano.estimate_dataset_size('demo_dataset/')
    print("Dataset Statistics:")
    print(f"  Files:      {dataset_stats['files']}")
    print(f"  Total words: {dataset_stats['words']:,}")
    print(f"  Size:       {dataset_stats['mb']:.2f} MB")
    print(f"  Avg/file:   {dataset_stats['avg_words_per_file']:,} words")
    print()

    # Show sample content
    if os.path.exists('demo_dataset/0001.txt'):
        print("Sample from first document:")
        print("-" * 70)
        with open('demo_dataset/0001.txt') as f:
            lines = f.readlines()
            print(f"URL: {lines[0].strip()}")
            print()
            content = ''.join(lines[2:])
            print(content[:300] + "...")
        print("-" * 70)


def demo_deduplication():
    """Demo 2: Deduplication in action."""
    print("\n\n")
    print("="*70)
    print("DEMO 2: Deduplication")
    print("="*70)
    print()

    # Create URLs with duplicates
    duplicate_urls = """
https://en.wikipedia.org/wiki/Python_(programming_language)
https://en.wikipedia.org/wiki/Python_(programming_language)
https://en.wikipedia.org/wiki/JavaScript
""".strip()

    with open('demo_dupes.txt', 'w') as f:
        f.write(duplicate_urls)

    print("Created demo_dupes.txt with 2 unique URLs + 1 duplicate")
    print()

    # Process
    stats = textnano.download_and_clean('demo_dupes.txt', 'demo_dedup/')

    print()
    print(f"✓ Unique:     {stats['success']}")
    print(f"⊘ Duplicates: {stats['duplicates']}")
    print()
    print("→ Deduplication works! Only unique documents saved.")


def demo_merge():
    """Demo 3: Merging datasets."""
    print("\n\n")
    print("="*70)
    print("DEMO 3: Merging Datasets")
    print("="*70)
    print()

    # Use existing datasets from previous demos
    if not os.path.exists('demo_dataset/') or not os.path.exists('demo_dedup/'):
        print("⊘ Skipping - need demo 1 and 2 to run first")
        return

    print("Merging demo_dataset/ and demo_dedup/ into demo_merged/")
    print()

    textnano.merge_datasets('demo_dataset/', 'demo_dedup/',
                           output_dir='demo_merged/')

    # Show stats
    merged_stats = textnano.estimate_dataset_size('demo_merged/')
    print()
    print(f"Merged dataset:")
    print(f"  Files: {merged_stats['files']}")
    print(f"  Words: {merged_stats['words']:,}")


def demo_programmatic():
    """Demo 4: Using textnano in Python code."""
    print("\n\n")
    print("="*70)
    print("DEMO 4: Programmatic Usage")
    print("="*70)
    print()

    print("Example: Building a custom dataset in Python")
    print()

    code = """
import textnano

# Method 1: From URL file
stats = textnano.download_and_clean('my_urls.txt', 'output/')
print(f"Downloaded {stats['success']} documents")

# Method 2: Download individual URLs
url = 'https://en.wikipedia.org/wiki/Artificial_intelligence'
text = textnano.download_text(url)
if text:
    print(f"Got {len(text.split())} words")

# Method 3: Get dataset statistics
stats = textnano.estimate_dataset_size('output/')
print(f"Total: {stats['words']:,} words in {stats['files']} files")
"""

    print(code)


def cleanup_demos():
    """Clean up demo files."""
    print("\n\n")
    print("="*70)
    print("Cleanup")
    print("="*70)
    print()

    import shutil

    files_to_remove = ['demo_urls.txt', 'demo_dupes.txt']
    dirs_to_remove = ['demo_dataset', 'demo_dedup', 'demo_merged']

    for f in files_to_remove:
        if os.path.exists(f):
            os.remove(f)
            print(f"✓ Removed {f}")

    for d in dirs_to_remove:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"✓ Removed {d}/")

    print()
    print("Demo cleanup complete!")


def main():
    """Run all demos."""
    import sys

    print("""
╔════════════════════════════════════════════════════════════════════╗
║                      textnano Demo Script                          ║
║                                                                    ║
║  This demonstrates the key features of textnano:                   ║
║  1. Basic downloading and cleaning                                 ║
║  2. Automatic deduplication                                        ║
║  3. Merging multiple datasets                                      ║
║  4. Programmatic usage examples                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    if len(sys.argv) > 1 and sys.argv[1] == 'cleanup':
        cleanup_demos()
        return

    try:
        # Run demos
        demo_basic()
        demo_deduplication()
        demo_merge()
        demo_programmatic()

        print("\n\n")
        print("="*70)
        print("All Demos Complete!")
        print("="*70)
        print()
        print("Created directories:")
        print("  demo_dataset/  - Basic dataset")
        print("  demo_dedup/    - Deduplication example")
        print("  demo_merged/   - Merged dataset")
        print()
        print("To clean up demo files:")
        print("  python demo_textnano.py cleanup")
        print()

    except KeyboardInterrupt:
        print("\n\nDemo interrupted!")
    except Exception as e:
        print(f"\n\nError: {e}")
        print("\nMake sure textnano.py is in the same directory!")


if __name__ == '__main__':
    main()
