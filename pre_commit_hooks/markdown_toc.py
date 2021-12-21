#!/usr/bin/env python3

"""Updates the markdown table of contents."""

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


def _update_toc(path: str) -> Optional[str]:
    """Updates the table of contents for a file."""
    with open(path) as f:
        contents = f.read()
    if "<!-- toc -->" not in contents:
        return None
    if "<!-- tocstop -->" not in contents:
        return "Missing tocstop"

    try:
        headers, _ = markdown_links.get_links(contents)
    except ValueError as e:
        return str(e)
    toc = ["<!-- toc -->\n\n## Table of contents\n"]
    for header in headers:
        if header.label.lower() == "table of contents":
            continue
        if header.level == 1:
            # This is the doc title; exclude it.
            continue

        indent = " " * 4 * (header.level - 2)
        toc.append(f"{indent}-   [{header.label}](#{header.anchor})")

    # Add a blank line after entries, if any.
    if len(toc) > 1:
        toc.append("")
    toc.append("<!-- tocstop -->")

    new_contents = re.sub(
        "<!-- toc -->.*?<!-- tocstop -->",
        "\n".join(toc),
        contents,
        count=1,
        flags=re.DOTALL,
    )
    if new_contents != contents:
        with open(path, "w") as f:
            f.write(new_contents)
    return None


def main(argv: Optional[List[str]] = None) -> int:
    if not argv:
        argv = sys.argv
    parsed_args = _parse_args(argv[1:])
    paths = parsed_args.paths

    exit_code = 0
    for path in paths:
        if not path.endswith(".md"):
            continue
        msg = _update_toc(path)
        if msg:
            print(f"Error in {path}: {msg}")
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
