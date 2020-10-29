# pre-commit-tool-hooks

<!--
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
-->

This repository contains hooks for use with [pre-commit](pre-commit.com).

## Table of contents

<!-- toc -->
<!-- tocstop -->

## Using pre-commit-tool-hooks with pre-commit

Add this to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/google/pre-commit-tool-hooks
  rev: v1.0.0 # Use the rev you want to point at.
  hooks:
      - id: check-copyright
      # - id: ...
```

## Hooks

### check-copyright

Verifies that files contain a copyright statement. Looks for a Google Apache 2.0
license by default. To customize, pass `--copyright=<text>`, using `YYYY` for
year substitution.

In `.pre-commit-config.yaml`, put:

```yaml
- id: check-copyright
  args:
      - --copyright
      - |+
          Copyright YYYY my organization
          with multiple lines
```

### markdown-toc

Generates a table of contents for Markdown files. This uses
[jonschlinkert/markdown-toc](https://github.com/jonschlinkert/markdown-toc) with
some adaptations for [Prettier](https://prettier.io/) pre-commit compatibility.

The markdown-toc tool can still be used manually with Prettier, because Prettier
will fix the bullet format, but during pre-commit the two will rewrite each
other.

In a markdown file, put:

```md
## Table of contents

<!-- toc -->
<!-- tocstop -->
```

In `.pre-commit-config.yaml`, put:

```yaml
- id: markdown-toc
```
