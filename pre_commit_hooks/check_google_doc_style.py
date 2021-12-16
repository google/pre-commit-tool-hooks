#!/usr/bin/env python3

"""Checks doc style against https://developers.google.com/style."""

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
import re
import sys
from typing import Generator, List, Optional, Tuple

_IGNORE_START = "<!-- google-doc-style-ignore -->"
_IGNORE_STOP = "<!-- google-doc-style-resume -->"

# These are from https://developers.google.com/style/word-list.
_REPLACERS = (
    ("blacklist", "blocklist"),
    ("cons", "disadvantages"),
    ("e.g.", "for example"),
    ("file name", "filename"),
    ("filesystem", "file system"),
    ("flag", "option"),
    ("flags", "options"),
    ("for instance", "for example"),
    ("i.e.", "that is"),
    ("pros", "advantages"),
    ("repo", "repository"),
    ("repos", "repositories"),
    ("tl;dr", "to summarize"),
    ("via", "by way of"),
    ("vice versa", "the other way around"),
    ("vs.", "versus"),
    ("whitelist", "allowlist"),
)


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parses command-line arguments and flags."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        metavar="PATH",
        nargs="+",
        help="One or more paths of files to check.",
    )
    return parser.parse_args(args=argv)


def build_replacers() -> Generator[Tuple[str, str], None, None]:
    """Builds replacement regex objects."""
    # Do uncapitalized first, because capitalized uses case-insensitive.
    for capitalize in (False, True):
        for before, after in _REPLACERS:
            if capitalize:
                flags = "(?i)"
                after = after.capitalize()
            else:
                flags = ""
            # This needs to handle abbreviations, such as `i.e.`, and so checks
            # for the full search word. It may be useful to optimize if this
            # becomes a performance issue.  Use negative lookbehind and
            # lookahead to ensure we have word breaks.
            yield (r"%s(?<!\w)%s(?!\w)" % (flags, re.escape(before)), after)


def _check_style(replacers: List[Tuple[str, str]], path: str) -> Optional[str]:
    """Checks documentation style for the given path.

    Returns errors, if any.
    """
    with open(path) as f:
        contents = f.read()

    lines = contents.split("\n")
    ignoring = False
    for index in range(len(lines)):
        line = lines[index]
        if line == _IGNORE_START:
            if ignoring:
                return "Found a repeated %r without a %r on line %d" % (
                    _IGNORE_START,
                    _IGNORE_STOP,
                    index + 1,
                )
            ignoring = True
        elif line == _IGNORE_STOP:
            if not ignoring:
                return "Found a %r without a preceding %r on line %d" % (
                    _IGNORE_STOP,
                    _IGNORE_START,
                    index + 1,
                )
            ignoring = False
        elif not ignoring:
            new_line = line
            for before, after in replacers:
                new_line = re.sub(before, after, new_line)
            lines[index] = new_line
    if ignoring:
        return "Found a %r without a stopping %r" % (
            _IGNORE_START,
            _IGNORE_STOP,
        )

    new_contents = "\n".join(lines)
    if new_contents != contents:
        with open(path, "w") as f:
            f.write(new_contents)
    return None


def main(argv: Optional[List[str]] = None) -> int:
    if not argv:
        argv = sys.argv
    parsed_args = _parse_args(argv[1:])
    paths = parsed_args.paths

    # Build the list of replacer regexes once, and re-use it for all files.
    replacers = list(build_replacers())

    exit_code = 0
    for path in paths:
        if not path.endswith(".md"):
            continue
        errors = _check_style(replacers, path)
        if errors:
            print("Errors in %r: %s" % (path, errors))
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
