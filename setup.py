"""
Setup script for Shopify SEO Tool package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="shopify-seo-tool",
    version="1.0.0",
    author="Joshua Hellewell",
    author_email="jhellewell1722@gmail.com",
    description="AI-powered SEO optimisation tool for Shopify product titles",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/shopify-seo-tool",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "shopify-seo=shopify_seo.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "shopify_seo": ["*.txt", "*.md"],
    },
)
