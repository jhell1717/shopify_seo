"""
Shopify SEO Tool - A Python package for optimising Shopify product titles using AI.
"""

__version__ = "1.0.0"
__author__ = "Joshua Hellewell"

from .processor import ShopifySEOProcessor
from .config import Config

__all__ = ["ShopifySEOProcessor", "Config"]
