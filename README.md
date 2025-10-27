# textnano - Minimal Text Dataset Builder

A **minimal** text dataset builder inspired by lazynlp.
Perfect for ML students who just want clean text datasets quickly.

## Features

✅ **Zero dependencies** - Pure Python stdlib

✅ **Simple API** - Easy to use and understand

✅ **Auto deduplication** - No duplicate documents

✅ **Clean text** - HTML removed, whitespace normalized

✅ **Smart filtering** - Excludes social media, images, videos by default

✅ **Built-in extractors** - Wikipedia, Reddit, Gutenberg support

## Installation

```bash
# Install from source
pip install -e .

# Or install from PyPI (when published)
pip install textnano
```

## Quick Start

### 1. Get some URLs

```bash
# Create a file with URLs (one per line)
cat > urls.txt << EOF
https://en.wikipedia.org/wiki/Machine_learning
https://en.wikipedia.org/wiki/Deep_learning
https://en.wikipedia.org/wiki/Natural_language_processing
https://www.gutenberg.org/files/1342/1342-h/1342-h.htm
EOF
```

### 2. Build dataset

```bash
# Download and clean
textnano urls urls.txt dataset/

# Output:
# Processing 4 URLs...
# [1/4] https://en.wikipedia.org/wiki/Machine_learning...
#   ✓ Saved (3421 words)
# [2/4] https://en.wikipedia.org/wiki/Deep_learning...
#   ✓ Saved (2890 words)
# ...
```

### 3. Use the dataset

```
dataset/
├── 0001.txt              # First document
├── 0002.txt              # Second document
├── 0003.txt
├── success.txt           # List of successful URLs
└── failed.txt            # List of failed URLs
```

Each .txt file format:
```
<URL>

<clean text content>
```

## Usage

### Command Line

```bash
# Basic usage (uses default filters)
textnano urls urls.txt output/

# Limit number of URLs
textnano urls urls.txt output/ 100

# Add custom exclusions
textnano urls urls.txt output/ --exclude-domains spam.com --exclude-extensions rar

# Disable default filters (only use your custom ones)
textnano urls urls.txt output/ --no-default-excludes --exclude-domains mysite.com

# Get statistics
textnano stats output/

# Merge multiple datasets
textnano merge dataset1/ dataset2/ merged/
```

### Built-in Extractors

Extract URLs from large data sources, then build datasets:

```bash
# Wikipedia (requires wikiextractor preprocessing)
# 1. Install wikiextractor: pip install wikiextractor
# 2. Extract from dump: python -m wikiextractor.WikiExtractor enwiki-latest.xml.bz2 --json -o wiki_json/
# 3. Extract URLs:
textnano wikipedia wiki_json/ --output wikipedia_urls.txt --max 10000
# 4. Build dataset:
textnano urls wikipedia_urls.txt wiki_dataset/

# Reddit (from pre-extracted URL files)
# 1. Download from: https://drive.google.com/file/d/1hRtA3zZ0K5UHKOQ0_8d0BIc_1VyxgY51/view
# 2. Extract and merge URLs:
textnano reddit reddit_urls/ --output reddit_urls.txt --max 5000
# 3. Build dataset:
textnano urls reddit_urls.txt reddit_dataset/

# Project Gutenberg
# 1. Generate URLs (checks each book ID):
textnano gutenberg --output gutenberg_urls.txt --max-id 1000
# 2. Build dataset:
textnano urls gutenberg_urls.txt books_dataset/
```

### Python API

```python
import textnano

# Download and clean (with default filters)
stats = textnano.download_and_clean('urls.txt', 'output/')
print(f"Success: {stats['success']}, Failed: {stats['failed']}, Excluded: {stats['excluded']}")

# Add custom exclusions
stats = textnano.download_and_clean(
    'urls.txt', 'output/',
    exclude_domains=['spam.com', 'ads.net'],
    exclude_extensions=['rar', 'exe']
)

# Disable default filters
stats = textnano.download_and_clean(
    'urls.txt', 'output/',
    use_default_excludes=False,
    exclude_domains=['mysite.com']
)

# Get dataset statistics
stats = textnano.estimate_dataset_size('output/')
print(f"Total: {stats['words']:,} words in {stats['files']} files")

# Merge datasets
textnano.merge_datasets('dataset1/', 'dataset2/', output_dir='merged/')
```

## What It Does

1. **Filters** - Excludes social media, images, videos (132 domains, 37 extensions by default)
2. **Downloads** - Fetches content from each URL
3. **Cleans** - Removes HTML tags, normalizes whitespace
4. **Filters length** - Skips documents with < 50 words
5. **Deduplicates** - Removes duplicate content
6. **Saves** - Numbered text files (0001.txt, 0002.txt, ...)

## Perfect For

- 🎓 ML students learning NLP
- 🔬 Quick research experiments
- 📚 Building small training datasets
- 🧪 Testing data pipelines
- 📝 Text analysis projects

## Example Datasets

### Wikipedia Articles
```bash
# Create URL list (example: top ML topics)
cat > ml_wikipedia.txt << EOF
https://en.wikipedia.org/wiki/Machine_learning
https://en.wikipedia.org/wiki/Deep_learning
https://en.wikipedia.org/wiki/Neural_network
https://en.wikipedia.org/wiki/Transformer_(machine_learning_model)
https://en.wikipedia.org/wiki/GPT-3
https://en.wikipedia.org/wiki/BERT_(language_model)
EOF

textnano ml_wikipedia.txt ml_dataset/
```

### Project Gutenberg Books
```bash
# Public domain books
cat > books.txt << EOF
https://www.gutenberg.org/files/1342/1342-h/1342-h.htm  # Pride and Prejudice
https://www.gutenberg.org/files/84/84-h/84-h.htm        # Frankenstein
https://www.gutenberg.org/files/11/11-h/11-h.htm        # Alice in Wonderland
EOF

textnano books.txt books_dataset/
```

### News Articles
```bash
# Note: Respect robots.txt and terms of service
cat > news.txt << EOF
https://example-news.com/article-1
https://example-news.com/article-2
EOF

textnano news.txt news_dataset/
```

## Parallel Processing

For large datasets, split and run in parallel:

```bash
# Split URLs into chunks
split -l 100 all_urls.txt chunk_

# Run multiple processes
for file in chunk_*; do
    textnano "$file" "output_$(basename $file)/" &
done
wait

# Merge results
textnano merge output_*/ final_dataset/
```

## Comparison

| Feature | textnano | lazynlp | beautifulsoup + requests |
|---------|----------|---------|--------------------------|
| **Files** | 1 | 5 | Your custom code |
| **LOC** | ~200 | ~800 | 100-200 (yours) |
| **Dependencies** | 0 | 2 | 2+ |
| **Learning time** | 5 min | 30 min | 1 hour |
| **Deduplication** | ✅ | ✅ | ❌ (you implement) |


### Integration with Pandas

```python
import textnano
import pandas as pd
from pathlib import Path

# Read dataset into DataFrame
def load_dataset(directory):
    data = []

    for file in sorted(Path(directory).glob('[0-9]*.txt')):
        with open(file) as f:
            lines = f.read().split('\n', 2)
            url = lines[0] if lines else ''
            text = lines[2] if len(lines) > 2 else ''

            data.append({
                'url': url,
                'text': text,
                'word_count': len(text.split())
            })

    return pd.DataFrame(data)

# Usage
df = load_dataset('dataset/')
print(df.describe())
print(df[df['word_count'] > 1000].head())
```

## FAQs

**Q: How do I get URLs?**
A: Create a .txt file with one URL per line. You can scrape them, use sitemap.xml, or manually curate.

**Q: What sites work best?**
A: Text-heavy sites work great: Wikipedia, blogs, news sites, Project Gutenberg. Avoid sites with heavy JavaScript.

**Q: How to handle rate limits?**
A: Add delays between requests by modifying the download loop, or split URLs and run at different times.

**Q: Can I use this for production?**
A: This is a learning tool. For production, use lazynlp or build a proper scraper with retry logic, robots.txt handling, etc.

**Q: How to cite this?**
A: This is a simplified educational version of lazynlp. Cite the original: https://github.com/chiphuyen/lazynlp

## Default Exclusions

By default, textnano excludes:

**Domains (132)**: Social media (reddit, twitter, instagram, etc.), image hosts (imgur, flickr, etc.), video platforms (youtube, vimeo, etc.), shopping sites (amazon, walmart, etc.)

**Extensions (37)**: Images (.jpg, .png, .gif), videos (.mp4, .mov), documents (.pdf, .doc), executables (.exe, .apk), archives (.zip, .tar)

Use `--no-default-excludes` to disable this behavior.

## Limitations

- No retry logic (fails on first error)
- No robots.txt checking
- No rate limiting
- Basic HTML cleaning (might miss some content)
- Simple deduplication (first 8 words only)

These are intentional simplifications for educational clarity.

## Extending textnano

Want to add features? Easy! The code is simple:

```python
# Add PDF support
import PyPDF2

def download_pdf_text(url):
    # Download PDF
    response = urllib.request.urlopen(url)
    pdf = PyPDF2.PdfReader(response)

    # Extract text
    text = ''
    for page in pdf.pages:
        text += page.extract_text()

    return text
```

## Real-World Examples

### Example 1: Build a Q&A Dataset

```python
# Download Stack Overflow questions
urls = [
    'https://stackoverflow.com/questions/...',
    # ... more URLs
]

with open('stackoverflow.txt', 'w') as f:
    for url in urls:
        f.write(url + '\n')

textnano.download_and_clean('stackoverflow.txt', 'qa_dataset/')
```

### Example 2: Documentation Dataset

```python
# Python documentation pages
import textnano

docs_urls = [
    'https://docs.python.org/3/library/os.html',
    'https://docs.python.org/3/library/sys.html',
    # ... more
]

# Save URLs
with open('python_docs.txt', 'w') as f:
    for url in docs_urls:
        f.write(url + '\n')

# Build dataset
textnano.download_and_clean('python_docs.txt', 'python_docs_dataset/')

# Use for training
stats = textnano.estimate_dataset_size('python_docs_dataset/')
print(f"Built dataset: {stats['words']:,} words")
```

## Credits

Inspired by [lazynlp](https://github.com/chiphuyen/lazynlp) by Chip Huyen.

## License

MIT License - Do whatever you want with it!

---
Happy dataset building! 🚀
