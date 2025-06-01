"""
Tests for the config module.
"""
from viajes import config


def test_openai_api_key_exists():
    """Test that OPENAI_API_KEY exists and is not empty."""
    assert config.OPENAI_API_KEY is not None
    assert config.OPENAI_API_KEY != ""


def test_supabase_config_exists():
    """Test that Supabase configuration exists and is not empty."""
    assert config.SUPABASE_URL is not None
    assert config.SUPABASE_URL != ""
    assert config.SUPABASE_KEY is not None
    assert config.SUPABASE_KEY != ""


def test_langfuse_config_exists():
    """Test that Langfuse configuration exists and is not empty."""
    assert config.LANGFUSE_PUBLIC_KEY is not None
    assert config.LANGFUSE_PUBLIC_KEY != ""
    assert config.LANGFUSE_SECRET_KEY is not None
    assert config.LANGFUSE_SECRET_KEY != ""
    assert config.LANGFUSE_HOST is not None
    assert config.LANGFUSE_HOST != ""
