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
