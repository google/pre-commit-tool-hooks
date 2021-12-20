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
from typing import Callable


def assert_exit_code(
    test_case: unittest.TestCase,
    test_call: Callable[[str], int],
    orig: str,
    expected: str,
    ext: str = ".md",
    exit_code: int = 0,
) -> None:
    with tempfile.NamedTemporaryFile(suffix=ext, mode="w", delete=False) as f:
        filename = f.name
        f.write(orig)
        f.flush()

    test_case.assertEqual(test_call(filename), exit_code)
    with open(filename) as updated_file:
        test_case.assertEqual(updated_file.read(), expected)

    os.unlink(filename)
