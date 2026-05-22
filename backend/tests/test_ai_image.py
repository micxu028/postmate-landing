"""Tests for AI image service — keyword extraction, URL building."""
from services.ai_image import _unsplash_url


class TestUnsplashUrl:

    def test_basic_prompt(self):
        url = _unsplash_url("A bright yoga studio with natural lighting")
        assert url.startswith("https://loremflickr.com/400/400/")
        assert "yoga" in url
        assert "studio" in url

    def test_short_prompt(self):
        url = _unsplash_url("Yoga class")
        assert "yoga" in url or "class" in url

    def test_stopwords_filtered(self):
        url = _unsplash_url("A photo of the studio with soft lighting")
        assert "photo" not in url
        assert "studio" in url

    def test_fallback_to_fitness(self):
        url = _unsplash_url("a an the")
        assert "fitness" in url
