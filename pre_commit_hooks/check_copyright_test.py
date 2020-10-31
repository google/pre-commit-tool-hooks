"""Tests for check_copyright.py."""

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

import tempfile
import unittest
from unittest import mock

from pre_commit_hooks import check_copyright


class FakeExitError(Exception):
    pass


def _fake_exit(message):
    raise FakeExitError(message)


class TestCheckCopyright(unittest.TestCase):
    def test_get_copyright(self):
        validator = check_copyright._CopyrightValidator(
            "test", check_copyright._DEFAULT_SKIP_PATTERN, None
        )
        self.assertEqual(
            validator._get_copyright("test.py")[1],
            '__copyright__ = """\ntest\n"""\n',
        )
        self.assertEqual(validator._get_copyright("LICENSE"), None)
        self.assertEqual(
            validator._get_copyright("foo.bar")[1],
            "# test\n",
        )

    def test_builtin(self):
        with tempfile.NamedTemporaryFile(
            suffix=".py", mode="w", delete=False
        ) as f:
            argv = ["bin", f.name, "--copyright=test"]
            f.write("non-copyright content\n")
            f.flush()
            self.assertEqual(check_copyright.main(argv=argv), 1)
            f.write('__copyright__ = """\ntest\n"""\n')
            f.flush()
            self.assertEqual(check_copyright.main(argv=argv), 0)

    def test_yyyy(self):
        with tempfile.NamedTemporaryFile(
            suffix=".py", mode="w", delete=False
        ) as f:
            argv = ["bin", f.name, "--copyright=test YYYY"]
            f.write("non-copyright content\n")
            f.flush()
            self.assertEqual(check_copyright.main(argv=argv), 1)
            f.write('__copyright__ = """\ntest 2010\n"""\n')
            f.flush()
            self.assertEqual(check_copyright.main(argv=argv), 0)

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(
            suffix=".py", mode="w", delete=False
        ) as f:
            argv = ["bin", f.name, "--copyright=test"]
            self.assertEqual(check_copyright.main(argv=argv), 0)

    def test_skip_pattern_invalid(self):
        with mock.patch(
            "pre_commit_hooks.check_copyright._exit", side_effect=_fake_exit
        ):
            argv = [
                "bin",
                "testfile",
                "--skip_pattern=\\",
            ]
            self.assertRaisesRegex(
                FakeExitError, "--skip_pattern", check_copyright.main, argv=argv
            )

    def test_skip_pattern(self):
        with tempfile.NamedTemporaryFile(
            suffix=".py", mode="w", delete=False
        ) as f:
            argv = ["bin", f.name, "--copyright=test"]
            f.write("non-copyright content\n")
            f.flush()
            self.assertEqual(check_copyright.main(argv=argv), 1)
            argv.append("--skip_pattern=\\.py$")
            self.assertEqual(check_copyright.main(argv=argv), 0)

    def test_custom_format_invalid(self):
        with mock.patch(
            "pre_commit_hooks.check_copyright._exit", side_effect=_fake_exit
        ):
            argv = [
                "bin",
                "testfile",
                "--custom_format",
                "\\",
                "",
                "",
                "",
            ]
            self.assertRaisesRegex(
                FakeExitError,
                "--custom_format",
                check_copyright.main,
                argv=argv,
            )

    def test_custom_format_all(self):
        with tempfile.NamedTemporaryFile(
            suffix=".py", mode="w", delete=False
        ) as f:
            argv = [
                "bin",
                f.name,
                "--copyright=test",
                "--custom_format",
                ".py",
                "prefix",
                "? ",
                "suffix",
            ]
            f.write("non-copyright content\n")
            f.flush()
            self.assertEqual(check_copyright.main(argv=argv), 1)
            f.write("prefix\n? test\nsuffix\n")
            f.flush()
            self.assertEqual(check_copyright.main(argv=argv), 0)

    def test_custom_format_per_line_only(self):
        with tempfile.NamedTemporaryFile(
            suffix=".py", mode="w", delete=False
        ) as f:
            argv = [
                "bin",
                f.name,
                "--copyright=test",
                "--custom_format",
                ".py",
                "",
                "? ",
                "",
            ]
            f.write("non-copyright content\n")
            f.flush()
            self.assertEqual(check_copyright.main(argv=argv), 1)
            f.write("? test\n")
            f.flush()
            self.assertEqual(check_copyright.main(argv=argv), 0)
