#!/usr/bin/env python3
"""Utility functions for textnano."""

import os
from pathlib import Path


def print_stats(stats, title="SUMMARY"):
    """Print formatted statistics."""
    print("\n" + "="*60)
    print(title)
    print("="*60)

    key_order = ['success', 'failed', 'too_short', 'duplicates', 'excluded']

    for key in key_order:
        if key in stats:
            label = key.replace('_', ' ').capitalize()
            print(f"{label:12s} {stats[key]:6d}")

    total = sum(stats.values())
    print(f"{'Total':12s} {total:6d}")
    print("="*60)


def estimate_dataset_size(output_dir):
    """Get statistics about the dataset."""
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


def merge_datasets(*dirs, output_dir, is_duplicate_func):
    """Merge multiple datasets and deduplicate."""
    os.makedirs(output_dir, exist_ok=True)

    seen_fingerprints = set()
    output_idx = 1

    for input_dir in dirs:
        txt_files = sorted(Path(input_dir).glob('[0-9]*.txt'))

        for file in txt_files:
            with open(file) as f:
                content = f.read()

            if is_duplicate_func(content, seen_fingerprints):
                continue

            output_file = os.path.join(output_dir, f"{output_idx:04d}.txt")
            with open(output_file, 'w') as f:
                f.write(content)

            output_idx += 1

    print(f"Merged {output_idx-1} unique documents from {len(dirs)} datasets")
