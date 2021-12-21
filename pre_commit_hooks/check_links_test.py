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

from pre_commit_hooks import check_links
from pre_commit_hooks import file_test_case


class TestMarkdownToc(file_test_case.FileTestCase):
    def setUp(self) -> None:
        self.setup_helper(
            lambda filename: check_links.main(argv=["bin", filename])
        )

    def test_wrong_ext(self) -> None:
        contents = "[test](#nonexistent)\n"
        self.assert_exit_code(contents, contents, ext=".py")

    def test_bad_link(self) -> None:
        contents = "[test](#nonexistent)"
        self.assert_exit_code(contents, contents, exit_code=1)

    def test_empty_file(self) -> None:
        self.assert_exit_code("", "")

    def test_simple_link(self) -> None:
        contents = "# Anchor\n\n[test](#anchor)"
        self.assert_exit_code(contents)

    def test_repeated_link(self) -> None:
        contents = "# Anchor\n\n## Anchor\n\n[test](#anchor-1)"
        self.assert_exit_code(contents)
