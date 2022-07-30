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
from typing import Any, Dict, List, NamedTuple, Tuple

import commonmark


class Header(NamedTuple):
    label: str
    anchor: str
    level: int


class Link(NamedTuple):
    label: str
    destination: str
    line_number: int


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


def _make_anchor(node: Any, used_anchors: Dict[str, int]) -> str:
    """Chooses the appropriate anchor name for a header label."""
    # Pick out the text fragments that the anchor will be based off.
    label_parts: List[str] = []
    for child, _ in node.walker():
        if child.t == "code":
            label_parts.append(child.literal)
        elif child.t == "text":
            label_parts.append(child.literal)

    anchor = "".join(label_parts).lower().strip()
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


def get_links(contents: str) -> Tuple[List[Header], List[Link]]:
    # Maps anchor tags to titles.
    headers: List[Header] = []
    links: List[Link] = []

    # Tracks the number of times a given anchor tag is used.
    used_anchors: Dict[str, int] = {}

    # Passive correctness checking on files.
    prev_level = 1
    prev_header = "(first header)"

    # The actual parser.
    md_parser = commonmark.Parser()
    root = md_parser.parse(contents)

    # Links don't have sourcepos set, so use the closest known location.
    last_line = -1
    for child, entering in root.walker():
        if child.sourcepos is not None:
            last_line = child.sourcepos[0][0]
        # We only look at nodes when entering them.
        if not entering:
            continue

        if child.t == "heading":
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
                Header(
                    label,
                    _make_anchor(child, used_anchors),
                    child.level,
                )
            )
        elif child.t == "link":
            assert child.destination is not None
            links.append(
                Link(_make_label(child), str(child.destination), last_line)
            )
    return (headers, links)
