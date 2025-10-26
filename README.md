# textnano - Minimal Text Dataset Builder

A **single-file** (~200 lines) text dataset builder inspired by lazynlp.
Perfect for ML students who just want clean text datasets quickly.

## Features

✅ **Zero dependencies** - Pure Python stdlib

✅ **Single file** - Just copy textnano.py

✅ **Simple API** - 3 functions, that's it

✅ **Auto deduplication** - No duplicate documents

✅ **Clean text** - HTML removed, whitespace normalized

✅ **Smart filtering** - Excludes social media, images, videos by default

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
textnano urls.txt dataset/

# Or without installation
python -m textnano urls.txt dataset/

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
# Basic (uses default filters)
textnano urls.txt output/

# Limit number of URLs
textnano urls.txt output/ 100

# Add custom exclusions
textnano urls.txt output/ --exclude-domains spam.com --exclude-extensions rar

# Disable default filters (only use your custom ones)
textnano urls.txt output/ --no-default-excludes --exclude-domains mysite.com

# Get statistics
textnano stats output/

# Merge multiple datasets
textnano merge dataset1/ dataset2/ merged/
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

## Advanced Tips

### Custom Cleaning

```python
import textnano

# Download text
text = textnano.download_text('https://example.com')

# Custom cleaning
text = text.lower()  # Lowercase
text = re.sub(r'[^a-z\s]', '', text)  # Only letters
# ... your processing

# Save
with open('output.txt', 'w') as f:
    f.write(text)
```

### Filter by Content

```python
import textnano

def download_with_filter(url_file, output_dir, keywords):
    """Only save documents containing certain keywords."""
    # Read URLs
    with open(url_file) as f:
        urls = [line.strip() for line in f]

    saved = 0
    for url in urls:
        text = textnano.download_text(url)

        # Check keywords
        if text and any(kw in text.lower() for kw in keywords):
            with open(f'{output_dir}/{saved:04d}.txt', 'w') as f:
                f.write(f"{url}\n\n{text}")
            saved += 1

    print(f"Saved {saved} matching documents")

# Usage
download_with_filter('urls.txt', 'filtered/', ['machine learning', 'neural'])
```

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

textnano is a simplified educational version - a single file that students can read, understand, and modify.

## License

MIT License - Do whatever you want with it!

## Learn More

- Read the code - it's only ~200 lines!
- Modify it for your use case
- Upgrade to [lazynlp](https://github.com/chiphuyen/lazynlp) for production

---

**Remember**: This is a learning tool. It teaches the core concepts of web scraping, text cleaning, and deduplication in a simple, readable way. For serious projects, use proper tools like lazynlp, Scrapy, or BeautifulSoup with robust error handling.

Happy dataset building! 🚀
