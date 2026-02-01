#!/usr/bin/env python3
"""
Setup configuration for ReconMaster - Automated Reconnaissance Framework

This setup.py enables installation via pip and packaging for PyPI distribution.

Usage:
    pip install .                    # Local installation
    pip install -e .                 # Editable installation for development
    python setup.py sdist bdist_wheel # Build distributions
    twine upload dist/*              # Upload to PyPI
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    with open(readme_file, encoding="utf-8") as f:
        long_description = f.read()

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
install_requires = []
if requirements_file.exists():
    with open(requirements_file, encoding="utf-8") as f:
        install_requires = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="reconmaster",
    version="1.0.0",
    author="ReconMaster Contributors",
    author_email="contact@reconmaster.dev",
    description="Automated Reconnaissance Framework for Security Testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ReconMaster",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/ReconMaster/issues",
        "Documentation": "https://github.com/yourusername/ReconMaster/wiki",
        "Source Code": "https://github.com/yourusername/ReconMaster",
    },
    license="MIT",
    
    # Package configuration
    packages=find_packages(include=["reconmaster", "reconmaster.*"]),
    py_modules=["reconmaster", "rate_limiter", "utils"],
    
    # Python version requirement
    python_requires=">=3.7",
    
    # Dependencies
    install_requires=install_requires,
    
    # Testing dependencies
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "pytest-timeout>=1.4",
            "black>=20.8b1",
            "flake8>=3.8",
            "mypy>=0.900",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "pytest-timeout>=1.4",
            "mock>=4.0",
        ],
    },
    
    # Entry points for command-line script
    entry_points={
        "console_scripts": [
            "reconmaster=reconmaster:main",
        ],
    },
    
    # Include additional files
    package_data={
        "": [
            "LEGAL.md",
            "CHANGELOG.md",
            "LICENSE",
            "wordlists/*.txt",
        ],
    },
    include_package_data=True,
    
    # Classifiers for PyPI
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities",
    ],
    
    # Keywords for searching
    keywords=[
        "reconnaissance",
        "security",
        "testing",
        "subdomain",
        "enumeration",
        "scanning",
        "penetration-testing",
        "infosec",
        "osint",
    ],
    
    # Additional metadata
    zip_safe=False,
)
