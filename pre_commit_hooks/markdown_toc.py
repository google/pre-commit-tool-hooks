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
import datetime
import os
import re
import sys

def _parse_args(argv=None):
    """Parses command-line arguments and flags."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', metavar="PATH", nargs="+", help="One or more paths of files to check.")
    return parser.parse_args(args=argv)


def update_toc(path):
    in_code_block = False
    with open(path) as f:
      contents = f.read()
    if '<!-- toc -->' not in contents:
      return

    toc = ['<!-- toc -->\n\n## Table of contents\n']
    prev_depth = 0
    prev_header = '(first header)'
    for line in contents.split('\n'):
      # Skip code blocks.
      if line.startswith('```'):
        in_code_block = not in_code_block
        continue
      if in_code_block:
        continue

      match = re.match(r'^(#+)\s*(.+)', line)
      if not match:
        continue
      depth = len(match.group(1))
      if depth - 1 > prev_depth:
        return 'Header %q has depth %d, which is too deep versus previous header %q with with depth %d.' % (line, depth, prev_header, depth)
      prev_depth = depth
      prev_header = line

      toc.append('%s-   %s' % ('    ' * (depth-1), match.group(2)))
    toc.append('\n<!-- tocstop -->')

    new_conents = re.sub('<!-- toc -->.*?<!-- tocstop -->', '\n'.join(toc), contents, count=1, flags=re.DOTALL)
    print(new_conents)


def main(argv=None):
    if not argv:
        argv = sys.argv
    parsed_args = _parse_args(argv[1:])
    paths = parsed_args.paths

    exit_code = 0
    for path in paths:
      if not path.endswith('.md'):
        continue
      update_toc(path)
    return 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
