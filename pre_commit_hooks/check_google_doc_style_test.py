"""Tests for check_google_doc_style.py."""

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
import tempfile
import unittest

from pre_commit_hooks import check_google_doc_style


class TestCheckGoogleDocStyle(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = 1000

    def _assert_contents(
        self, orig: str, expected: str, ext: str = ".md", exit_code: int = 0
    ) -> None:
        with tempfile.NamedTemporaryFile(
            suffix=ext, mode="w", delete=False
        ) as f:
            filename = f.name
            f.write(orig)
            f.flush()

        self.assertEqual(
            check_google_doc_style.main(argv=["bin", filename]), exit_code
        )
        with open(filename) as updated_file:
            self.assertEqual(updated_file.read(), expected)

        os.unlink(filename)

    def test_wrong_ext(self) -> None:
        contents = "Something\n\ncons:\n\n- Example"
        self._assert_contents(contents, contents, ext=".py")

    def test_noop(self) -> None:
        contents = "Do nothing."
        self._assert_contents(contents, contents)

    def test_basic(self) -> None:
        before = "Something\n\ncons:\n\n- Example"
        after = "Something\n\ndisadvantages:\n\n- Example"
        self._assert_contents(before, after)

    def test_basic_capitalize(self) -> None:
        before = "Something\n\nCons:\n\n- Example"
        after = "Something\n\nDisadvantages:\n\n- Example"
        self._assert_contents(before, after)

    def test_basic_uppercase(self) -> None:
        before = "Something\n\nCONS:\n\n- Example"
        after = "Something\n\nDisadvantages:\n\n- Example"
        self._assert_contents(before, after)

    def test_repeated(self) -> None:
        before = "cons cons Cons CONS"
        after = "disadvantages disadvantages Disadvantages Disadvantages"
        self._assert_contents(before, after)

    def test_abbreviation(self) -> None:
        before = "Programming languages, e.g., C++"
        after = "Programming languages, for example, C++"
        self._assert_contents(before, after)

    def test_abbreviation_capitalize(self) -> None:
        before = "Programming languages. E.g., C++"
        after = "Programming languages. For example, C++"
        self._assert_contents(before, after)

    def test_ignore(self) -> None:
        before = (
            "Cons\n"
            "<!-- google-doc-style-ignore -->\n"
            "Cons\n"
            "<!-- google-doc-style-resume -->\n"
            "Cons"
        )
        after = (
            "Disadvantages\n"
            "<!-- google-doc-style-ignore -->\n"
            "Cons\n"
            "<!-- google-doc-style-resume -->\n"
            "Disadvantages"
        )
        self._assert_contents(before, after)

    def test_ignore_missing_start(self) -> None:
        contents = "Cons\n<!-- google-doc-style-resume -->\nCons"
        self._assert_contents(contents, contents, exit_code=1)

    def test_ignore_missing_end(self) -> None:
        contents = "Cons\n<!-- google-doc-style-ignore -->\nCons"
        self._assert_contents(contents, contents, exit_code=1)

    def test_ignore_repeated(self) -> None:
        contents = (
            "Cons\n"
            "<!-- google-doc-style-ignore -->\n"
            "<!-- google-doc-style-ignore -->\n"
            "<!-- google-doc-style-resume -->\n"
            "Cons"
        )
        self._assert_contents(contents, contents, exit_code=1)
