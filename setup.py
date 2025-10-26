#!/usr/bin/env python3
"""
setup.py for textnano - Minimal text dataset builder
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="textnano",
    version="0.1.0",
    description="Minimal text dataset builder - Zero dependencies, single file, perfect for ML students",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rustem",
    author_email="rustem@example.com",
    url="https://github.com/Rustem/textnano",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        # Zero dependencies - pure Python stdlib!
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "textnano=textnano.core:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="text dataset nlp machine-learning web-scraping data-collection",
    project_urls={
        "Bug Reports": "https://github.com/Rustem/textnano/issues",
        "Source": "https://github.com/Rustem/textnano",
    },
)
