# textnano - 30 Second Quick Start

## Install
```bash
pip install -e .
# Or use directly: python -m textnano
```

## Run (3 steps)
```bash
# 1. Create URL list
echo "https://en.wikipedia.org/wiki/Machine_learning" > urls.txt

# 2. Download (automatically filters social media, images, videos)
textnano urls.txt dataset/

# 3. Done!
ls dataset/
# → 0001.txt, success.txt, failed.txt
```

## Advanced Usage
```bash
# Add custom exclusions
textnano urls.txt dataset/ --exclude-domains spam.com --exclude-extensions rar

# Disable default filters
textnano urls.txt dataset/ --no-default-excludes

# Limit URLs
textnano urls.txt dataset/ 100
```

## That's it!

Want more examples? See [README.md](README.md)

Want to try it? Run:
```bash
python textnano/examples/demo_textnano.py
```
