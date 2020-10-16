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

from pre_commit_hooks import check_copyright


class TestCheckCopyright(unittest.TestCase):
    def test_copyright_validator(self):
        validator = check_copyright._CopyrightValidator("test")
        self.assertEqual(
            validator._get_copyright("test.py")[1],
            '__copyright__ = """\ntest\n"""\n'
        )
        self.assertEqual(validator._get_copyright("LICENSE"), None)
        self.assertEqual(
            validator._get_copyright("foo.bar")[1],
            '# test\n',
        )

    def test_main(self):
        with tempfile.NamedTemporaryFile(
            suffix=".py", mode="w", delete=False
        ) as f:
            argv = ["bin", f.name, "--copyright=test"]
            self.assertEqual(check_copyright.main(argv=argv), 0)
            f.write("non-copyright content\n")
            f.flush()
            self.assertEqual(check_copyright.main(argv=argv), 1)
            f.write('__copyright__ = """\ntest\n"""\n')
            f.flush()
            self.assertEqual(check_copyright.main(argv=argv), 0)
