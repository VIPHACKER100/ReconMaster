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
    version = "3.1.0",
    author="VIPHACKER100",
    author_email="contact@reconmaster.dev",
    description="Professional-Grade Automated Reconnaissance Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VIPHACKER100/ReconMaster",
    project_urls={
        "Bug Tracker": "https://github.com/VIPHACKER100/ReconMaster/issues",
        "Source Code": "https://github.com/VIPHACKER100/ReconMaster",
        "Security Policy": "https://github.com/VIPHACKER100/ReconMaster/blob/main/SECURITY.md",
    },
    license="MIT",
    
    # Package configuration
    packages=find_packages(),
    py_modules=["reconmaster", "utils", "rate_limiter"],
    
    # Python version requirement
    python_requires=">=3.9",
    
    # Dependencies
    install_requires=install_requires,
    
    # Testing dependencies
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "pytest-timeout>=2.1",
            "black>=23.1",
            "flake8>=6.0",
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
            "LICENSE",
            "SECURITY.md",
            "CHANGELOG.md",
            "wordlists/*.txt",
            "plugins/*.py",
        ],
    },
    include_package_data=True,
    
    # Classifiers for PyPI
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
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
