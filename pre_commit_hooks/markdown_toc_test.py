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

import unittest

from pre_commit_hooks import markdown_toc
from pre_commit_hooks import test_utils


class TestMarkdownToc(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = 1000
        self._test_call = lambda filename: markdown_toc.main(
            argv=["bin", filename]
        )

    def test_wrong_ext(self) -> None:
        contents = "<!-- toc --><!-- tocstop -->\n"
        test_utils.assert_exit_code(
            self, self._test_call, contents, contents, ext=".py"
        )

    def test_bad_header_level(self) -> None:
        contents = "<!-- toc --><!-- tocstop -->\n### Test"
        test_utils.assert_exit_code(
            self, self._test_call, contents, contents, exit_code=1
        )

    def test_empty_file(self) -> None:
        test_utils.assert_exit_code(self, self._test_call, "", "")

    def test_empty_toc(self) -> None:
        before = "<!-- toc --><!-- tocstop -->\n"
        after = "<!-- toc -->\n\n## Table of contents\n\n<!-- tocstop -->\n"
        test_utils.assert_exit_code(self, self._test_call, before, after)
        test_utils.assert_exit_code(self, self._test_call, after, after)

    def test_basic_toc(self) -> None:
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
        test_utils.assert_exit_code(self, self._test_call, before, after)
        test_utils.assert_exit_code(self, self._test_call, after, after)

    def test_codeblock_toc(self) -> None:
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
        test_utils.assert_exit_code(self, self._test_call, before, after)
        test_utils.assert_exit_code(self, self._test_call, after, after)

    def test_weird_toc(self) -> None:
        header = "# Header\n\n<!-- toc -->"
        toc = (
            "\n\n## Table of contents\n\n"
            "-   [Advanced Find & Replace](#advanced-find--replace)\n"
            "-   [Package as `package`](#package-as-package)\n"
            "-   [Something _italicized_](#something-_italicized_)\n"
            "-   [Something **bolded**](#something-bolded)\n"
            "-   [Some _nested **chars `here`** now_]"
            "(#some-_nested-chars-here-now_)\n"
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
        test_utils.assert_exit_code(self, self._test_call, before, after)
        test_utils.assert_exit_code(self, self._test_call, after, after)

    def test_repeating_toc(self) -> None:
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
        test_utils.assert_exit_code(self, self._test_call, before, after)
        test_utils.assert_exit_code(self, self._test_call, after, after)
