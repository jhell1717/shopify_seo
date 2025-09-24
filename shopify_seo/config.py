"""
Configuration management for Shopify SEO tool.
"""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration class for Shopify SEO processor."""
    
    # AI Model Configuration
    model_name: str = "gpt-oss:latest"
    max_title_length: int = 53
    
    # File Configuration
    temp_dir: str = "temp"
    allowed_extensions: tuple = ('.csv',)
    max_file_size: int = 16 * 1024 * 1024  # 16MB
    
    # API Configuration
    api_timeout: int = 30
    max_retries: int = 3
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables."""
        return cls(
            model_name=os.getenv('SHOPIFY_SEO_MODEL', cls.model_name),
            max_title_length=int(os.getenv('SHOPIFY_SEO_MAX_TITLE_LENGTH', str(cls.max_title_length))),
            temp_dir=os.getenv('SHOPIFY_SEO_TEMP_DIR', cls.temp_dir),
            api_timeout=int(os.getenv('SHOPIFY_SEO_API_TIMEOUT', str(cls.api_timeout))),
            max_retries=int(os.getenv('SHOPIFY_SEO_MAX_RETRIES', str(cls.max_retries)))
        )
