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
                markdown_links.Header("Header", "header", 1),
                markdown_links.Header("Section", "section", 2),
                markdown_links.Header("More", "more", 3),
                markdown_links.Header("Even more", "even-more", 3),
                markdown_links.Header("Other section", "other-section", 2),
            ],
            headers,
        )
        self.assertListEqual([], links)

    def test_punctuation(self) -> None:
        contents = "# Header? Yes it is!\n"
        headers, links = markdown_links.get_links(contents)
        self.assertListEqual(
            [
                markdown_links.Header(
                    "Header? Yes it is!", "header-yes-it-is", 1
                ),
            ],
            headers,
        )
        self.assertListEqual([], links)

    def test_formatting(self) -> None:
        contents = (
            "## Package as `package`\n\n"
            "## Something _italicized_\n\n"
            "## Something **bolded**\n\n"
            "## Some _nested **chars `here`** now_\n\n"
        )
        headers, links = markdown_links.get_links(contents)
        self.assertListEqual(
            [
                markdown_links.Header(
                    "Package as `package`", "package-as-package", 2
                ),
                markdown_links.Header(
                    "Something _italicized_", "something-italicized", 2
                ),
                markdown_links.Header(
                    "Something **bolded**", "something-bolded", 2
                ),
                markdown_links.Header(
                    "Some _nested **chars `here`** now_",
                    "some-nested-chars-here-now",
                    2,
                ),
            ],
            headers,
        )
        self.assertListEqual([], links)

    def test_duplicates(self) -> None:
        contents = "# Header\n\n## Header\n\n"
        headers, links = markdown_links.get_links(contents)
        self.assertListEqual(
            [
                markdown_links.Header("Header", "header", 1),
                markdown_links.Header("Header", "header-1", 2),
            ],
            headers,
        )
        self.assertListEqual([], links)

    def test_bad_header(self) -> None:
        contents = "### Blah\n\n"
        self.assertRaises(ValueError, markdown_links.get_links, contents)

    def test_links(self) -> None:
        contents = "[test](#test)\n\n[test2](/test2)"
        headers, links = markdown_links.get_links(contents)
        self.assertListEqual([], headers)
        self.assertListEqual(
            [
                markdown_links.Link("test", "#test", 1),
                markdown_links.Link("test2", "/test2", 3),
            ],
            links,
        )
