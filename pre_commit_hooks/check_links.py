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
from pathlib import Path
import subprocess
import sys
from typing import Dict, List, Optional, Set, Tuple
from urllib import parse

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
    parser.add_argument(
        "--anchors-only",
        action="store_true",
        help="Set to only validate intra-document anchors, ignoring "
        " cross-document links.",
    )
    return parser.parse_args(args=argv)


def _print_error(path: str, link: markdown_links.Link, message: str) -> None:
    """Prints a link error."""
    print(
        f"{path}:{link.line_number}: "
        f"[{link.label}]({link.destination}): "
        f"{message}"
    )


class LinkCache(object):
    """Caches links for a file so that checks don't repeatedly parse files."""

    def __init__(self) -> None:
        self._cache: Dict[Path, Tuple[Set[str], List[markdown_links.Link]]] = {}

    def get(self, path: Path) -> Tuple[Set[str], List[markdown_links.Link]]:
        assert path.is_absolute(), path
        if path not in self._cache:
            with open(path) as f:
                contents = f.read()
            headers, links = markdown_links.get_links(contents)
            anchors = set([header.anchor for header in headers])
            self._cache[path] = (anchors, links)
        return self._cache[path]


def _check_links(
    link_cache: LinkCache, repo_root: Path, path: str, anchors_only: bool
) -> bool:
    """Validates links in the given file, returning true on errors."""
    absolute_path = Path(path).resolve()
    anchors, links = link_cache.get(absolute_path)

    has_errors = False
    for link in links:
        dest_url = parse.urlsplit(link.destination)
        if dest_url.scheme:
            # If a scheme (such as https:) is specified, don't check further.
            continue
        elif dest_url.netloc:
            _print_error(
                path, link, "Link is missing a scheme, such as https://."
            )
            has_errors = True
        elif dest_url.path:
            if not anchors_only:
                url_path = Path(dest_url.path)
                if url_path.is_absolute():
                    # Absolute paths are actually relative to the repo root.
                    dest_path = repo_root.joinpath(dest_url.path.lstrip("/"))
                else:
                    # Relative paths are relative to the current file's dir.
                    dest_path = absolute_path.parent.joinpath(url_path)
                if dest_path.is_dir():
                    # If it's pointing at a directory, we only validate further
                    # if there's a fragment -- that implies it's actually
                    # linking a README.md.
                    if not dest_url.fragment:
                        continue
                    dest_path = dest_path.joinpath("README.md")
                # Verify the file exists.
                if not dest_path.is_file():
                    _print_error(
                        path, link, "Link points at a non-existent file."
                    )
                    has_errors = True
                    continue
                # Check anchors.
                if (
                    dest_url.fragment
                    and dest_url.fragment not in link_cache.get(dest_path)[0]
                ):
                    _print_error(
                        path, link, "Link points at a non-existent anchor."
                    )
                    has_errors = True
                    continue
        elif dest_url.fragment:
            # There's only a fragment, so it's an internal anchor.
            if dest_url.fragment not in anchors:
                _print_error(
                    path, link, "Link points at a non-existent anchor."
                )
                has_errors = True
    return has_errors


def main(argv: Optional[List[str]] = None) -> int:
    if not argv:
        argv = sys.argv
    parsed_args = _parse_args(argv[1:])
    paths = parsed_args.paths

    repo_root = Path(
        subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
        .rstrip()
        .decode("utf-8")
    )

    link_cache = LinkCache()
    exit_code = 0
    for path in paths:
        if not path.endswith(".md"):
            continue
        if _check_links(link_cache, repo_root, path, parsed_args.anchors_only):
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
