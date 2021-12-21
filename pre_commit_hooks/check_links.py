"""Validates links in markdown files."""

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

import argparse
import sys
from typing import List, Optional

from pre_commit_hooks import markdown_links


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


def _check_links(path: str) -> bool:
    """Updates the table of contents for a file."""
    with open(path) as f:
        contents = f.read()
    headers, links = markdown_links.get_links(contents)

    anchors = set([header.anchor for header in headers])

    has_errors = False
    for link in links:
        if link.destination.startswith("#"):
            anchor = link.destination[1:]
            if anchor not in anchors:
                print(
                    f"{path}:{link.line_number}: "
                    f"[{link.label}]({link.destination}) "
                    f"points at a non-existent anchor."
                )
                has_errors = True
        # TODO: Handle other link forms.
    return has_errors


def main(argv: Optional[List[str]] = None) -> int:
    if not argv:
        argv = sys.argv
    parsed_args = _parse_args(argv[1:])
    paths = parsed_args.paths

    exit_code = 0
    for path in paths:
        if not path.endswith(".md"):
            continue
        if _check_links(path):
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
