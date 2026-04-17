#!/usr/bin/env python3
"""Basic tests for Phantom Vision CLI."""

import json
import base64
import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO
from PIL import Image


def make_dummy_b64_image() -> tuple[str, str]:
    img = Image.new("RGB", (100, 100), color=(73, 109, 137))
    buf = BytesIO()
    img.save(buf, format="JPEG")
    b64 = base64.standard_b64encode(buf.getvalue()).decode()
    return b64, "image/jpeg"


class TestBuildVisionMessage(unittest.TestCase):
    def test_structure(self):
        from phantom import build_vision_message
        b64, mt = make_dummy_b64_image()
        msgs = build_vision_message(b64, mt, "Describe this.")
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["role"], "user")
        content = msgs[0]["content"]
        self.assertEqual(content[0]["type"], "image")
        self.assertEqual(content[1]["type"], "text")
        self.assertEqual(content[1]["text"], "Describe this.")


class TestTagParsing(unittest.TestCase):
    def test_valid_json_tags(self):
        raw = '["sunset", "ocean", "peaceful", "blue"]'
        tags = json.loads(raw.strip())
        self.assertIsInstance(tags, list)
        self.assertIn("sunset", tags)

    def test_fallback_tag_parsing(self):
        raw = '"sunset", "ocean", "peaceful"'
        tags = [t.strip().strip('"') for t in raw.split(",")]
        self.assertEqual(tags[0], "sunset")


if __name__ == "__main__":
    unittest.main()
