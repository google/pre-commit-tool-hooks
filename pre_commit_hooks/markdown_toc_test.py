"""Tests for markdown_toc.py."""

__copyright__ = """
Copyright 2020 Google LLC

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

import os
import re
import tempfile
import unittest

from pre_commit_hooks import markdown_toc


class TestMarkdownToc(unittest.TestCase):
    def setUp(self):
        self.maxDiff = 1000

    def _assert_contents(self, orig, expected, ext=".md"):
        with tempfile.NamedTemporaryFile(
            suffix=ext, mode="w", delete=False
        ) as f:
            filename = f.name
            f.write(orig)
            f.flush()

        self.assertEqual(markdown_toc.main(argv=["bin", filename]), 0)
        with open(filename) as f:
            self.assertEqual(f.read(), expected)

        os.unlink(filename)

    def test_wrong_ext(self):
        contents = "<!-- toc --><!-- tocstop -->\n"
        self._assert_contents(contents, contents, ext=".py")

    def test_empty_file(self):
        self._assert_contents("", "")

    def test_empty_toc(self):
        before = "<!-- toc --><!-- tocstop -->\n"
        after = "<!-- toc -->\n\n## Table of contents\n\n<!-- tocstop -->\n"
        self._assert_contents(before, after)
        self._assert_contents(after, after)

    def test_basic_toc(self):
        header = "# Header\n\n<!-- toc -->"
        toc = (
            "\n\n## Table of contents\n\n"
            "-   [Section](#section)\n"
            "    -   [More](#more)\n"
            "    -   [Even more](#even-more)\n"
            "-   [Other section](#other-section)\n"
            "\n"
        )
        body = (
            "<!-- tocstop -->\n\n"
            "## Section\n\n"
            "text\n\n"
            "### More\n\n"
            "### Even more\n\n"
            "## Other section\n\n"
        )
        before = header + body
        after = header + toc + body
        self._assert_contents(before, after)
        self._assert_contents(after, after)

    def test_codeblock_toc(self):
        header = "# Header\n\n<!-- toc -->"
        toc = (
            "\n\n## Table of contents\n\n"
            "-   [Section](#section)\n"
            "    -   [More](#more)\n"
            "\n"
        )
        body = (
            "<!-- tocstop -->\n\n"
            "## Section\n\n"
            "text\n\n"
            "```\n"
            "## Ignored\n"
            "```\n"
            "### More\n\n"
        )
        before = header + body
        after = header + toc + body
        self._assert_contents(before, after)
        self._assert_contents(after, after)

    def test_weird_toc(self):
        header = "# Header\n\n<!-- toc -->"
        toc = (
            "\n\n## Table of contents\n\n"
            "-   [Advanced Find & Replace](#advanced-find--replace)\n"
            "-   [Package as `package`](#package-as-package)\n"
            "-   [Something _italicized_](#something-_italicized_)\n"
            "-   [Something **bolded**](#something-bolded)\n"
            "-   [Some _nested **chars `here`** now_](#some-_nested-chars-here-now_)\n"
            "\n"
        )
        body = (
            "<!-- tocstop -->\n\n"
            "## Advanced Find & Replace\n\n"
            "## Package as `package`\n\n"
            "## Something _italicized_\n\n"
            "## Something **bolded**\n\n"
            "## Some _nested **chars `here`** now_\n\n"
        )
        before = header + body
        after = header + toc + body
        self._assert_contents(before, after)
        self._assert_contents(after, after)

    def test_repeating_toc(self):
        header = "# Header\n\n<!-- toc -->"
        toc = (
            "\n\n## Table of contents\n\n"
            "-   [Bork](#bork)\n"
            "-   [Bork](#bork-1)\n"
            "-   [Bork](#bork-2)\n"
            "\n"
        )
        body = "<!-- tocstop -->\n\n## Bork\n\n## Bork\n\n## Bork\n\n"
        before = header + body
        after = header + toc + body
        self._assert_contents(before, after)
        self._assert_contents(after, after)
