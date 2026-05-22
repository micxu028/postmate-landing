"""Tests for AI text service — prompt building, JSON extraction."""
import json
from services.ai_text import _parse_json_response


class TestParseJsonResponse:

    def test_extract_from_code_block(self):
        text = "```json\n[{\"day\": 0, \"caption\": \"hello\"}]\n```"
        result = _parse_json_response(text)
        assert result is not None
        assert result[0]["day"] == 0

    def test_extract_plain_array(self):
        text = '[{"day": 0, "caption": "test", "hashtags": ["#a"]}]'
        result = _parse_json_response(text)
        assert result is not None
        assert result[0]["caption"] == "test"

    def test_extract_with_leading_text(self):
        text = "Here are your posts:\n[{\"day\":0,\"caption\":\"hello\"}]\nEnjoy!"
        result = _parse_json_response(text)
        assert result is not None
        assert result[0]["day"] == 0

    def test_extract_empty_text(self):
        import pytest
        with pytest.raises((json.JSONDecodeError, Exception)):
            _parse_json_response("")

    def test_extract_no_json(self):
        import pytest
        with pytest.raises((json.JSONDecodeError, Exception)):
            _parse_json_response("Just some text without JSON")

    def test_extract_backtick_without_json(self):
        text = "```\n[{\"day\": 1}]\n```"
        result = _parse_json_response(text)
        assert result is not None
        assert result[0]["day"] == 1

    def test_extract_multiple_objects(self):
        text = '[{"day":0},{"day":1},{"day":2}]'
        result = _parse_json_response(text)
        assert result is not None
        assert len(result) == 3
