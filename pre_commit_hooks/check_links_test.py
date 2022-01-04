"""Tests for check_links.py."""

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

from pathlib import Path
import tempfile
from typing import List
from unittest import mock

from pre_commit_hooks import check_links
from pre_commit_hooks import file_test_case


class TestMarkdownToc(file_test_case.FileTestCase):
    def setUp(self) -> None:
        self.setup_helper(
            lambda filename: check_links.main(
                argv=["bin"] + self._flags + [filename]
            )
        )

        self._flags: List[str] = []

        self._root_temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir = tempfile.TemporaryDirectory(
            dir=self._root_temp_dir.name
        )

        self._error_patcher = mock.patch(
            "pre_commit_hooks.check_links._print_error"
        )
        self._print_error = self._error_patcher.start()
        self._subprocess_patcher = mock.patch(
            "pre_commit_hooks.check_links.subprocess.check_output"
        )
        self._check_output = self._subprocess_patcher.start()
        self._check_output.return_value = self._root_temp_dir.name.encode()

    def tearDown(self) -> None:
        self._print_error.stop()
        self._subprocess_patcher.stop()

    def _assert_success(self, contents: str) -> None:
        self.assert_exit_code(contents)
        self._print_error.assert_not_called()

    def _assert_error(self, contents: str, error: str) -> None:
        self.assert_exit_code(contents, exit_code=1)
        self._print_error.assert_called_once()
        self.assertEqual(self._print_error.call_args.args[2], error)

    def _write(self, filename: str, contents: str) -> None:
        readme_path = Path(self._root_temp_dir.name).joinpath(filename)
        readme_path.write_text(contents)

    def test_wrong_ext(self) -> None:
        self.assert_exit_code("[test](#nonexistent)\n", ext=".py")
        self._print_error.assert_not_called()

    def test_bad_link(self) -> None:
        self._assert_error(
            "[test](#nonexistent)", "Link points at a non-existent anchor."
        )

    def test_bad_link_anchors_only(self) -> None:
        self._flags = ["--anchors-only"]
        self._assert_error(
            "[test](#nonexistent)", "Link points at a non-existent anchor."
        )

    def test_empty_file(self) -> None:
        self._assert_success("")

    def test_simple_link(self) -> None:
        self._assert_success("# Anchor\n\n[test](#anchor)")

    def test_repeated_link(self) -> None:
        self._assert_success("# Anchor\n\n## Anchor\n\n[test](#anchor-1)")

    def test_ignore_url(self) -> None:
        self._assert_success("[test](http://foo.com)")

    def test_invalid_url(self) -> None:
        self._assert_success("[test](http://foo:40xyz/)")

    def test_no_scheme(self) -> None:
        self._assert_error(
            "[test](//foo)", "Link is missing a scheme, such as https://."
        )

    def test_dir_link(self) -> None:
        self._assert_success("[test](/)")

    def test_implicit_readme(self) -> None:
        self._write("README.md", "# Foo\n")
        self._assert_success("[test](/#foo)")

    def test_implicit_readme_file_missing(self) -> None:
        self._assert_error(
            "[test](/#foo)", "Link points at a non-existent file."
        )

    def test_implicit_readme_anchor_missing(self) -> None:
        self._write("README.md", "blah\n")
        self._assert_error(
            "[test](/#foo)", "Link points at a non-existent anchor."
        )

    def test_absolute(self) -> None:
        self._write("test.md", "foo")
        self._assert_success("[test](/test.md)")

    def test_absolute_file_missing(self) -> None:
        self._assert_error(
            "[test](/test.md)", "Link points at a non-existent file."
        )

    def test_absolute_file_missing_anchors_only(self) -> None:
        self._flags = ["--anchors-only"]
        self._assert_success("[test](/test.md)")

    def test_absolute_anchor(self) -> None:
        self._write("test.md", "# Foo")
        self._assert_success("[test](/test.md#foo)")

    def test_absolute_anchor_missing(self) -> None:
        self._write("test.md", "foo")
        self._assert_error(
            "[test](/test.md#foo)", "Link points at a non-existent anchor."
        )

    def test_relative(self) -> None:
        self._write("test.md", "foo")
        self._assert_success("[test](../test.md)")

    def test_relative_file_missing(self) -> None:
        self._assert_error(
            "[test](../test.md)", "Link points at a non-existent file."
        )

    def test_relative_anchor(self) -> None:
        self._write("test.md", "# Foo")
        self._assert_success("[test](../test.md#foo)")

    def test_relative_anchor_missing(self) -> None:
        self._write("test.md", "foo")
        self._assert_error(
            "[test](../test.md#foo)", "Link points at a non-existent anchor."
        )
