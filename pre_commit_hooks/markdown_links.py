"""Library for loading links from a markdown file."""

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

import re
from typing import Any, Dict, List, Tuple

import commonmark


def _make_label(node: Any) -> str:
    """Makes a label from a node. Handles joining common children."""
    label: List[str] = []
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


def _make_anchor(label: str, used_anchors: Dict[str, int]) -> str:
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


def get_links(contents: str) -> Tuple[List[Tuple[str, str, int]], List[str]]:
    # Maps anchor tags to titles.
    headers: List[Tuple[str, str, int]] = []
    links: List[str] = []

    # Tracks the number of times a given anchor tag is used.
    used_anchors: Dict[str, int] = {}

    # Passive correctness checking on files.
    prev_level = 1
    prev_header = "(first header)"

    # The actual parser.
    md_parser = commonmark.Parser()
    root = md_parser.parse(contents)

    for child, entering in root.walker():
        if not entering or child.t != "heading":
            continue

        label = _make_label(child)

        if child.level - 1 > prev_level:
            raise ValueError(
                "Header %r has level %d, which is too deep versus previous "
                "header %r with level %d."
                % (label, child.level, prev_header, prev_level)
            )
        prev_level = child.level
        prev_header = label

        headers.append(
            (
                _make_anchor(label, used_anchors),
                label,
                child.level,
            )
        )
    return (headers, links)
