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

This repository contains hooks for use with [pre-commit](http://pre-commit.com).

<!-- toc -->

## Table of contents

-   [Using pre-commit-tool-hooks with pre-commit](#using-pre-commit-tool-hooks-with-pre-commit)
-   [Hooks](#hooks)
    -   [check-copyright](#check-copyright)
        -   [Customizing copyright formats](#customizing-copyright-formats)
    -   [check-google-doc-style](#check-google-doc-style)
    -   [check-links](#check-links)
    -   [markdown-toc](#markdown-toc)

<!-- tocstop -->

## Using pre-commit-tool-hooks with pre-commit

Add this to your `.pre-commit-config.yaml`:

<!-- google-doc-style-ignore -->
<!-- Ignoring due to 'repo' in yaml -->

```yaml
- repo: https://github.com/google/pre-commit-tool-hooks
  rev: vTODO # Use the rev you want to point at.
  hooks:
      - id: check-copyright
      # - id: ...
```

<!-- google-doc-style-resume -->

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

#### Customizing copyright formats

`--custom_format` overrides copyright formatting for a given path pattern. It
may be specified multiple times to override multiple path patterns. The first
matching `--custom_format` will be used; if none match, the built-in copyright
defaults will be used.

`--custom_format` takes four arguments:

1.  `PATH_PATTERN`: A path regex that must match the input path.
2.  `PREFIX`: A prefix block for the copyright.
3.  `PER_LINE_PREFIX`: The per-line prefix for the copyright.
4.  `SUFFIX`: A suffix block for the copyright.

If a prefix or suffix is not desired, pass an empty string.

For example, to get JavaScript copyright formatting like:

```js
/**
 * Copyright
 */
```

Do:

```yaml
- id: check-copyright
  args:
      - --custom_format
      - '\.js$'
      - '/**'
      - ' * '
      - ' */'
```

To instead get formatting like:

```js
// Copyright
```

Do:

```yaml
- id: check-copyright
  args:
      - --custom_format
      - '\.js$'
      - ''
      - '// '
      - ''
```

Escaping is not generally supported, but `\-` is required to escape a starting
`-`. For example, to get HTML-style comments, the closing `-->` must be escaped:

```yaml
- id: check-copyright
  args:
      - --custom_format
      - '\.plist$'
      - '<!--'
      - ''
      - '\-->'
```

### check-google-doc-style

Checks documentation against the
[Google developer documentation style guide](http://developers.google.com/style),
with a principle of automatically generating fixes over erroring for manual
edits. Note, while no manual fixes are requested today, some may be added in the
future.

This does not handle reformatting of edits. Please use a tool like
[Prettier](https://prettier.io) to fix formatting.

In `.pre-commit-config.yaml`, put:

```yaml
- id: check-google-doc-style
```

To disable this on sections of a markdown file, use the ignore/resume comments:

```md
Checked

<!-- google-doc-style-ignore -->

Ignored

<!-- google-doc-style-resume -->

Checked
```

### check-links

Checks links for correctness. For example, ensures that markdown links point at
valid anchors within the doc.

`--anchors-only` may be passed to only validate intra-document anchors. In other
words, cross-document links such as `/foo.md#bar` will not be validated (even to
see if foo.md exists) while `#bar` will be validated to ensure a `Bar` header
exists within the checked document.

In `.pre-commit-config.yaml`, put:

```yaml
- id: check-links
```

### markdown-toc

Generates a [Prettier](https://prettier.io)-compatible table of contents for
Markdown files.

In a markdown file, put the `<!-- toc -->` and `<!-- tocstop -->` markers to
indicate where to put the table of contents:

```md
# Document title

<!-- toc -->
<!-- tocstop -->

## Header

### Sub-header
```

This will generate a table of contents based on non-title headers:

```md
# Document title

<!-- toc -->

## Table of contents

-   [Header](#header)
    -   [Sub-header](#sub-header)

<!-- toc -->

## Header

### Sub-header
```

In `.pre-commit-config.yaml`, put:

```yaml
- id: markdown-toc
```

This generates bullets with a four space indent. When used with Prettier, it's
recommended to specify the `tabWidth` in `.prettierrc.yaml` to match:

```yaml
overrides:
    - files: '*.md'
      options:
          tabWidth: 4
```
