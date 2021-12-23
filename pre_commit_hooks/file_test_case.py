"""Utilities for tests."""

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
from typing import Callable, Optional


class FileTestCase(unittest.TestCase):
    def setup_helper(self, test_call: Callable[[str], int]) -> None:
        self.maxDiff = 1000
        self._test_call = test_call
        self.temp_dir: Optional[tempfile.TemporaryDirectory] = None

    def assert_exit_code(
        self,
        orig: str,
        expected: Optional[str] = None,
        ext: str = ".md",
        exit_code: int = 0,
    ) -> None:
        if expected is None:
            expected = orig

        dir_name = None
        if self.temp_dir:
            dir_name = self.temp_dir.name
        with tempfile.NamedTemporaryFile(
            suffix=ext, mode="w", delete=False, dir=dir_name
        ) as f:
            filename = f.name
            f.write(orig)
            f.flush()

        self.assertEqual(self._test_call(filename), exit_code)
        with open(filename) as updated_file:
            self.assertEqual(updated_file.read(), expected)

        os.unlink(filename)
