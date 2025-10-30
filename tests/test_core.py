#!/usr/bin/env python3
"""
Unit tests for textnano core functionality
"""

import unittest
import tempfile
import os
from pathlib import Path

from textnano.core import (
    clean_html,
    text_fingerprint,
    is_duplicate,
    download_and_clean
)


class TestCleanHTML(unittest.TestCase):
    """Test HTML cleaning functionality"""

    def test_remove_script_tags(self):
        """Test that script tags are removed"""
        html = '<html><script>alert("test")</script><p>Content</p></html>'
        result = clean_html(html)
        self.assertNotIn('script', result)
        self.assertNotIn('alert', result)
        self.assertIn('Content', result)

    def test_remove_style_tags(self):
        """Test that style tags are removed"""
        html = '<html><style>body { color: red; }</style><p>Content</p></html>'
        result = clean_html(html)
        self.assertNotIn('style', result)
        self.assertNotIn('color', result)
        self.assertIn('Content', result)

    def test_remove_html_tags(self):
        """Test that HTML tags are removed"""
        html = '<div><p>Hello <strong>World</strong></p></div>'
        result = clean_html(html)
        self.assertNotIn('<', result)
        self.assertNotIn('>', result)
        self.assertIn('Hello', result)
        self.assertIn('World', result)

    def test_unescape_html_entities(self):
        """Test that HTML entities are unescaped"""
        html = '<p>&amp; &quot;quotes&quot; &copy; 2024</p>'
        result = clean_html(html)
        self.assertIn('&', result)
        self.assertIn('"quotes"', result)
        self.assertIn('©', result)

    def test_normalize_whitespace(self):
        """Test that whitespace is normalized"""
        html = '<p>Too    many     spaces</p>'
        result = clean_html(html)
        self.assertEqual('Too many spaces', result.strip())

    def test_empty_html(self):
        """Test that empty HTML returns empty string"""
        html = '<html><body></body></html>'
        result = clean_html(html)
        self.assertEqual('', result)

    def test_nested_script_tags(self):
        """Test removal of nested script tags"""
        html = '<html><body><div><script>var x = 1;</script>Text</div></body></html>'
        result = clean_html(html)
        self.assertNotIn('script', result)
        self.assertNotIn('var x', result)
        self.assertIn('Text', result)


class TestTextFingerprint(unittest.TestCase):
    """Test text fingerprinting functionality"""

    def test_same_text_same_fingerprint(self):
        """Test that same text produces same fingerprint"""
        text = "This is a test sentence with some words"
        fp1 = text_fingerprint(text)
        fp2 = text_fingerprint(text)
        self.assertEqual(fp1, fp2)

    def test_different_text_different_fingerprint(self):
        """Test that different text produces different fingerprints"""
        text1 = "This is the first text"
        text2 = "This is the second text"
        fp1 = text_fingerprint(text1)
        fp2 = text_fingerprint(text2)
        self.assertNotEqual(fp1, fp2)

    def test_case_insensitive(self):
        """Test that fingerprinting is case insensitive"""
        text1 = "Hello World Test"
        text2 = "hello world test"
        fp1 = text_fingerprint(text1)
        fp2 = text_fingerprint(text2)
        self.assertEqual(fp1, fp2)

    def test_custom_n_words(self):
        """Test that custom n parameter works"""
        text = "one two three four five six seven eight nine ten"
        fp1 = text_fingerprint(text, n=3)
        fp2 = text_fingerprint(text, n=5)
        # Different n values should potentially give different fingerprints
        # unless the first n words are the same
        self.assertIsNotNone(fp1)
        self.assertIsNotNone(fp2)

    def test_short_text(self):
        """Test fingerprinting with text shorter than n words"""
        text = "short"
        fp = text_fingerprint(text, n=10)
        self.assertIsNotNone(fp)
        self.assertIsInstance(fp, str)

    def test_fingerprint_format(self):
        """Test that fingerprint is a valid MD5 hash"""
        text = "test text"
        fp = text_fingerprint(text)
        self.assertEqual(len(fp), 32)  # MD5 hash length
        self.assertTrue(all(c in '0123456789abcdef' for c in fp))


class TestIsDuplicate(unittest.TestCase):
    """Test duplicate detection functionality"""

    def test_first_text_not_duplicate(self):
        """Test that first text is not marked as duplicate"""
        seen = set()
        text = "This is a unique text"
        result = is_duplicate(text, seen)
        self.assertFalse(result)
        self.assertEqual(len(seen), 1)

    def test_same_text_is_duplicate(self):
        """Test that same text is marked as duplicate"""
        seen = set()
        text = "This is a test text"
        is_duplicate(text, seen)  # First time
        result = is_duplicate(text, seen)  # Second time
        self.assertTrue(result)

    def test_different_texts_not_duplicate(self):
        """Test that different texts are not duplicates"""
        seen = set()
        text1 = "First unique text"
        text2 = "Second unique text"
        result1 = is_duplicate(text1, seen)
        result2 = is_duplicate(text2, seen)
        self.assertFalse(result1)
        self.assertFalse(result2)
        self.assertEqual(len(seen), 2)

    def test_case_insensitive_duplicate(self):
        """Test that duplicate detection is case insensitive"""
        seen = set()
        text1 = "Hello World Test"
        text2 = "hello world test"
        is_duplicate(text1, seen)
        result = is_duplicate(text2, seen)
        self.assertTrue(result)


class TestDownloadAndClean(unittest.TestCase):
    """Test end-to-end download and clean functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.urls_file = os.path.join(self.temp_dir, 'urls.txt')
        self.output_dir = os.path.join(self.temp_dir, 'output')

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_empty_url_file(self):
        """Test handling of empty URL file"""
        # Create empty URL file
        with open(self.urls_file, 'w') as f:
            f.write('')

        stats = download_and_clean(self.urls_file, self.output_dir)

        self.assertEqual(stats['success'], 0)
        self.assertEqual(stats['failed'], 0)

    def test_output_directory_created(self):
        """Test that output directory is created"""
        with open(self.urls_file, 'w') as f:
            f.write('https://example.com\n')

        download_and_clean(self.urls_file, self.output_dir)

        self.assertTrue(os.path.exists(self.output_dir))

    def test_log_files_created(self):
        """Test that success and failed log files are created"""
        with open(self.urls_file, 'w') as f:
            f.write('https://example.com\n')

        download_and_clean(self.urls_file, self.output_dir)

        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'success.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'failed.txt')))

    def test_max_urls_limit(self):
        """Test that max_urls parameter limits processing"""
        with open(self.urls_file, 'w') as f:
            for i in range(10):
                f.write(f'https://example{i}.com\n')

        stats = download_and_clean(self.urls_file, self.output_dir, max_urls=3)

        # Should only attempt 3 URLs
        total = stats['success'] + stats['failed'] + stats['excluded']
        self.assertLessEqual(total, 3)

    def test_domain_exclusion(self):
        """Test that excluded domains are filtered out"""
        with open(self.urls_file, 'w') as f:
            f.write('https://twitter.com/test\n')
            f.write('https://example.com\n')

        stats = download_and_clean(
            self.urls_file,
            self.output_dir,
            exclude_domains=['twitter.com'],
            use_default_excludes=False
        )

        self.assertGreater(stats['excluded'], 0)

    def test_extension_exclusion(self):
        """Test that excluded extensions are filtered out"""
        with open(self.urls_file, 'w') as f:
            f.write('https://example.com/file.pdf\n')
            f.write('https://example.com/page\n')

        stats = download_and_clean(
            self.urls_file,
            self.output_dir,
            exclude_extensions=['pdf'],
            use_default_excludes=False
        )

        self.assertGreater(stats['excluded'], 0)

    def test_stats_structure(self):
        """Test that returned stats have correct structure"""
        with open(self.urls_file, 'w') as f:
            f.write('https://example.com\n')

        stats = download_and_clean(self.urls_file, self.output_dir)

        self.assertIn('success', stats)
        self.assertIn('failed', stats)
        self.assertIn('duplicates', stats)
        self.assertIn('too_short', stats)
        self.assertIn('excluded', stats)


if __name__ == '__main__':
    unittest.main()
