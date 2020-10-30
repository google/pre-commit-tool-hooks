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

<!-- toc -->

## Table of contents

-   [Using pre-commit-tool-hooks with pre-commit](#using-pre-commit-tool-hooks-with-pre-commit)
-   [Hooks](#hooks)
    -   [check-copyright](#check-copyright)
    -   [markdown-toc](#markdown-toc)

<!-- tocstop -->

## Using pre-commit-tool-hooks with pre-commit

Add this to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/google/pre-commit-tool-hooks
  rev: v1.0.5 # Use the rev you want to point at.
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

Generates a [Prettier](https://pretter.io)-compatible table of contents for
Markdown files.

In a markdown file, put:

```md
<!-- toc -->
<!-- tocstop -->
```

This will generate:

```md
<!-- toc -->

## Table of contents

-   [Header](#header)
    -   [Sub-header](#sub-header)

<!-- toc -->
```

In `.pre-commit-config.yaml`, put:

```yaml
- id: markdown-toc
```

When used with Prettier, it's recommended to specify the `tabWidth` in
`.prettierrc.yaml` to match:

```yaml
overrides:
    - files: '*.md'
      options:
          tabWidth: 4
```
