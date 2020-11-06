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
import datetime
import os
import re
import sys
import textwrap

import mistune


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


def _check_style(path):
    """Checks documentation style for the given path.

    Returns a list of errors, if any.
    """
    errors = []

    md = mistune.Markdown(mistune.AstRenderer())
    tokens = md.parse(contents)


def main(argv=None):
    if not argv:
        argv = sys.argv
    parsed_args = _parse_args(argv[1:])
    paths = parsed_args.paths

    exit_code = 0
    for path in paths:
        if not path.endswith(".md"):
            continue
        errors = _check_style(path)
        if errors:
            print("Errors in `%s`: %s" % (path, errors))
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
