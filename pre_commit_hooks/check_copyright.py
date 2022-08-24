#!/usr/bin/env python3

"""Checks that files contain copyrights."""

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

import argparse
import datetime
import os
import re
import sys
import textwrap
from typing import List, Optional, Tuple

_DEFAULT_COPYRIGHT = """Copyright YYYY Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""


_DEFAULT_SKIP_PATTERN = r"(?:^LICENSE|\.(?:ico|json))$"
_BUILTIN_FORMATS = (
    (r"\.(cpp|h)$", "", "// ", ""),
    (r"\.(html|md)$", "<!--", "", "-->"),
    (r"\.js$", "/*", " * ", " */"),
    (r"\.py$", '__copyright__ = """', "", '"""'),
    # Hash-commented copyrights make a good default for most file types.
    ("", "", "# ", ""),
)


def _exit(error: str) -> None:
    """A simple exit wrapper for testing."""
    sys.exit(error)


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parses command-line arguments and flags."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--copyright",
        metavar="COPYRIGHT",
        default=_DEFAULT_COPYRIGHT,
        help="The copyright to check for. Use `YYYY` to insert the current "
        "year. Defaults to a Google Apache 2.0 license.",
    )
    parser.add_argument(
        "--custom_format",
        dest="custom_formats",
        metavar=("PATH_PATTERN", "PREFIX", "PER_LINE_PREFIX", "SUFFIX"),
        action="append",
        nargs=4,
        help="Overrides copyright formatting for a given path pattern. It may "
        "be specified multiple times to override multiple path patterns. The "
        "first matching pattern will be used; if none match, the built-in "
        "copyright defaults will be used.",
    )
    parser.add_argument(
        "--skip_pattern",
        metavar="PATH_PATTERN",
        default=_DEFAULT_SKIP_PATTERN,
        help="A path pattern for paths to skip. Defaults to `%s`."
        % _DEFAULT_SKIP_PATTERN,
    )
    parser.add_argument(
        "paths",
        metavar="PATH",
        nargs="+",
        help="One or more paths of files to check.",
    )
    return parser.parse_args(args=argv)


class _CopyrightValidator(object):
    def __init__(
        self,
        copyright: str,
        skip_pattern: str,
        custom_formats: Optional[List[List[str]]],
    ) -> None:
        """Initializes the list of copyright formats and skipped paths."""
        copyright = copyright.strip("\n")
        try:
            self._skip = re.compile(skip_pattern)
        except re.error as e:
            _exit("Invalid --skip_pattern `%s`: %s`" % (skip_pattern, e))

        self._formats: List[Tuple[re.Pattern, re.Pattern, str]] = []
        if custom_formats:
            for custom_format in custom_formats:
                for i, x in enumerate(custom_format):
                    # Dashes are treated as flags by argparse, so special-case
                    # an escape.
                    if x.startswith(r"\-"):
                        custom_format[i] = x[1:]
                self._add_format(copyright, *custom_format)
        for builtin_format in _BUILTIN_FORMATS:
            self._add_format(copyright, *builtin_format)

    def _add_format(
        self,
        copyright: str,
        path_pattern: str,
        prefix: str,
        per_line_prefix: str,
        suffix: str,
    ) -> None:
        """Adds a format, either from --custom_format or built-in.

        This will reformat the standard copyright based on the prefix,
        per_line_prefix, and suffix.

        The output tuple contains a regex for paths, a regex for matching
        copyrights, and the suggested copyright that will be printed.
        """
        try:
            path_re = re.compile(path_pattern)
        except re.error as e:
            _exit(
                "Invalid --custom_format pattern `%s`: %s`" % (path_pattern, e)
            )

        formatted = textwrap.indent(copyright, per_line_prefix)
        formatted = formatted.replace(
            "\n\n", "\n%s\n" % per_line_prefix.rstrip(" ")
        )
        if prefix:
            formatted = "%s\n%s" % (prefix, formatted)
        if suffix:
            formatted = "%s\n%s" % (formatted, suffix)
        formatted += "\n"

        copyright_re = re.compile(re.escape(formatted).replace("YYYY", r"\d+"))
        suggest = formatted.replace("YYYY", str(datetime.datetime.now().year))

        self._formats.append((path_re, copyright_re, suggest))

    def _get_copyright(self, path: str) -> Optional[Tuple[re.Pattern, str]]:
        """Returns the copyright for the given path, or None to skip."""
        if self._skip.search(path):
            return None

        for path_re, copyright_re, suggest in self._formats:
            if not path_re.search(path):
                continue
            return (copyright_re, suggest)
            break
        raise ValueError(
            "Should have had at least a default match: `%s`" % path
        )

    def validate(self, path: str) -> bool:
        """Checks the file for a copyright, returning False on error."""
        if os.path.isdir(path):
            return True

        copyright = self._get_copyright(path)
        if not copyright:
            return True

        with open(path) as f:
            try:
                contents = f.read()
            except UnicodeDecodeError as e:
                print("Skipping %s: %s\n" % (path, e))
                return True

        # Skip empty files, such as __init__.py.
        if len(contents) <= 1:
            return True

        if copyright[0].search(contents):
            return True

        print(
            "Missing copyright in %s:\n%s" % (path, copyright[1]),
            file=sys.stderr,
        )
        return False


def main(argv: Optional[List[str]] = None) -> int:
    if not argv:
        argv = sys.argv
    parsed_args = _parse_args(argv[1:])
    copyright_validator = _CopyrightValidator(
        parsed_args.copyright,
        parsed_args.skip_pattern,
        parsed_args.custom_formats,
    )
    paths = parsed_args.paths

    exit_code = 0
    for path in paths:
        if not copyright_validator.validate(path):
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
