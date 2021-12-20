"""Tests for markdown_links.py."""

__copyright__ = """
Copyright 2021 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest

from pre_commit_hooks import markdown_links


class TestMarkdownLinks(unittest.TestCase):
    def test_empty(self) -> None:
        contents = "\n"
        self.assertEqual(([], []), markdown_links.get_links(contents))

    def test_example(self) -> None:
        contents = (
            "# Header\n\n"
            "## Section\n\n"
            "text\n\n"
            "### More\n\n"
            "### Even more\n\n"
            "## Other section\n\n"
        )
        headers, links = markdown_links.get_links(contents)
        self.assertListEqual(
            [
                ("header", "Header", 1),
                ("section", "Section", 2),
                ("more", "More", 3),
                ("even-more", "Even more", 3),
                ("other-section", "Other section", 2),
            ],
            headers,
        )

    def test_punctuation(self) -> None:
        contents = "# Header? Yes it is!\n"
        headers, links = markdown_links.get_links(contents)
        self.assertListEqual(
            [
                ("header-yes-it-is", "Header? Yes it is!", 1),
            ],
            headers,
        )

    def test_duplicates(self) -> None:
        contents = "# Header\n\n## Header\n\n"
        headers, links = markdown_links.get_links(contents)
        self.assertListEqual(
            [
                ("header", "Header", 1),
                ("header-1", "Header", 2),
            ],
            headers,
        )

    def test_bad(self) -> None:
        contents = "### Blah\n\n"
        self.assertRaises(ValueError, markdown_links.get_links, contents)
