# textnano - 30 Second Quick Start

## Install (copy one file)
```bash
curl -O https://raw.githubusercontent.com/yourusername/textnano/main/textnano.py
```

## Run (3 steps)
```bash
# 1. Create URL list
echo "https://en.wikipedia.org/wiki/Machine_learning" > urls.txt

# 2. Download
python textnano.py urls.txt dataset/

# 3. Done!
ls dataset/
# → 0001.txt, success.txt, failed.txt
```

## That's it!

Want more examples? See [README.md](README.md)

Want to try it? Run:
```bash
python textnano/examples/demo_textnano.py
```
