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

import commonmark


def _parse_args(argv=None):
    """Parses command-line arguments and flags."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        metavar="PATH",
        nargs="+",
        help="One or more paths of files to check.",
    )
    return parser.parse_args(args=argv)


def _make_label(node):
    """Makes a label from a node. Handles joining common children."""
    label = []
    for child, entering in node.walker():
        if child.t == "code":
            label.extend(("`", child.literal, "`"))
        elif child.t == "strong":
            label.append("**")
        elif child.t == "emph":
            label.append("_")
        elif child.t == "text":
            label.append(child.literal)
    return "".join(label)


def _make_anchor(label, used_anchors):
    """Chooses the appropriate anchor name for a header label."""
    anchor = label.lower().strip()
    # Imitate GFM anchors. Sadly, the exact format isn't clearly documented
    # anywhere, so this based on experimentation and what others have done to
    # successfully replicate the GitHub anchor mapping.
    anchor = anchor.replace(" ", "-")
    anchor = re.sub("[!\"#$%&'()*+,./:;<=>?@[\\\\\\]^`{|}~]", "", anchor)

    # Enumerate anchors when reused.
    if anchor in used_anchors:
        used_anchors[anchor] += 1
        anchor = "%s-%d" % (anchor, used_anchors[anchor])
    else:
        used_anchors[anchor] = 0

    return anchor


def _update_toc(path):
    """Updates the table of contents for a file."""
    with open(path) as f:
        contents = f.read()
    if "<!-- toc -->" not in contents:
        return
    if "<!-- tocstop -->" not in contents:
        return "Missing tocstop"

    toc = ["<!-- toc -->\n\n## Table of contents\n"]
    used_anchors = {}
    prev_level = 1
    prev_header = "(first header)"
    md_parser = commonmark.Parser()
    root = md_parser.parse(contents)
    for child, entering in root.walker():
        if not entering or child.t != "heading":
            continue

        label = _make_label(child)
        print(label, entering)
        if label.lower() == "table of contents":
            continue

        if child.level - 1 > prev_level:
            return (
                "Header %r has level %d, which is too deep versus previous "
                "header %r with level %d."
                % (label, child.level, prev_header, prev_level)
            )
        prev_level = child.level
        prev_header = label

        if child.level == 1:
            # This is the doc title; exclude it.
            continue

        toc.append(
            "%s-   [%s](#%s)"
            % (
                "    " * (child.level - 2),
                label,
                _make_anchor(label, used_anchors),
            )
        )

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


def main(argv=None):
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
            print("Error in %r: %s" % (path, msg))
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
