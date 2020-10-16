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


def _parse_args(argv=None):
    """Parses command-line arguments and flags."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--copyright",
        metavar="COPYRIGHT",
        default=_DEFAULT_COPYRIGHT,
        help="The copyright to check for. Use `YYYY` to insert the current year. Defaults to a Google Apache 2.0 license.")
    parser.add_argument('paths', metavar="PATH", nargs="+", help="One or more paths of files to check.")
    return parser.parse_args(args=argv)


def _prefix_copyright(copyright, prefix):
  """Returns a copyright with a new prefix string."""
  prefixed = textwrap.indent(copyright, prefix)
  prefixed = prefixed.replace("\n\n", "\n%s\n" % prefix.rstrip(" "))
  return prefixed + "\n";


def _copyright_matcher(copyright):
  """Takes the YYYY and returns a tuple of regexp and current year forms."""
  regexp = re.compile(re.escape(copyright).replace("YYYY", r"\d+"))
  suggest = copyright.replace("YYYY", str(datetime.datetime.now().year))
  return regexp, suggest


class _CopyrightValidator(object):
  def __init__(self, copyright):
    copyright = copyright.strip("\n")

    # Hash copyrights work for most files.
    self.default = _copyright_matcher(_prefix_copyright(copyright, "# "))

    slash_copyright = _copyright_matcher(_prefix_copyright(copyright, "// "))
    self.by_ext = {
        ".cpp": slash_copyright,
        ".h": slash_copyright,
        ".js": "/*\n%s\n*/" % copyright,
        ".json": None,  # Comments not supported.
        ".md": _copyright_matcher("<!--\n%s\n-->\n" % copyright),
        ".py": _copyright_matcher('__copyright__ = """\n%s\n"""\n' % copyright),
    }

  def _get_copyright(self, path):
    """Returns the copyright file for the given path, or None to skip."""
    if os.path.basename(path) == "LICENSE":
        return None

    _, ext = os.path.splitext(path)
    if ext in self.by_ext:
      return self.by_ext[ext]

    return self.default

  def validate(self, path):
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
            print('Skipping %s: %s\n' % (path, e))
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

def main(argv=None):
    if not argv:
        argv = sys.argv
    parsed_args = _parse_args(argv[1:])
    copyright_validator = _CopyrightValidator(parsed_args.copyright)
    paths = parsed_args.paths

    exit_code = 0
    for path in paths:
      if not copyright_validator.validate(path):
        exit_code =1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
