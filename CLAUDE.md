# CLAUDE.md — TTP (Template Text Parser)

## What is TTP?

TTP is a Python library for parsing semi-structured text into structured data using templates. It dynamically builds regexes from human-readable templates, matches them against input text, and produces structured results (dictionaries/lists) in formats like JSON, YAML, CSV, etc.

**Repository:** https://github.com/dmulyalin/ttp  
**Documentation:** https://ttp.readthedocs.io/  
**License:** MIT  
**Python:** 3.9+

## Project Structure

```
ttp/                    # Main package
  ttp.py                # Core module — all main classes (~3700 lines)
  __init__.py           # Package init, exposes the `ttp` class
  match/                # Match variable functions (re_, set_, lookup, joinmatches, ip, etc.)
  group/                # Group functions (contains, exclude, macro, validate, to_ip, etc.)
  variable/             # Template variable functions (getfilename, gethostname, time_funcs)
  input/                # Input plugins (commands, macro, test)
  output/               # Output plugins (deepdiffer, is_equal, macro, validate_cerberus, etc.)
  formatters/           # Output formatters (json, yaml, csv, pprint, table, tabulate, excel, jinja2, n2g)
  returners/            # Result returners (file, self, terminal, syslog)
  lookup/               # Lookup plugins (geoip2)
  patterns/             # Built-in regex patterns (get_pattern)
  utils/                # Utilities (attribute parsing, loaders, guessing, quick_parse)
test/                   # Tests
  pytest/               # All pytest test files (24 files)
docs/                   # Sphinx documentation
  source/               # RST source files
Data/                   # Sample data files for testing
```

### Key Classes in `ttp/ttp.py`

- **`ttp`** — Main public API class. Loads data/templates, runs parsing, returns results.
- **`_template_class`** — Represents a parsed `<template>` block. Holds groups, inputs, outputs, variables, lookups, macros.
- **`_input_class`** — Manages input data loading and filtering.
- **`_group_class`** — Represents a `<group>` block. Builds regex patterns from template lines, tracks hierarchy.
- **`_variable_class`** — Handles `<vars>` blocks and template variables.
- **`_parser_class`** — Core parsing engine. Runs regexes against text, applies match functions, builds result trees.
- **`_results_class`** — Manages result accumulation, grouping, and hierarchy formation.
- **`_outputter_class`** — Applies output functions and formatters, returns results via returners.
- **`_worker`** — Multiprocessing worker for parallel parsing.
- **`CachedModule`** — Lazy-loading module proxy with pickle-based caching.

### Plugin Architecture

All plugin directories (`match/`, `group/`, `output/`, `formatters/`, `returners/`, `variable/`, `input/`, `lookup/`) follow the same pattern:
- Each `.py` file is a plugin loaded on demand via `lazy_import_functions()`.
- Functions are registered in a global `_ttp_` dictionary keyed by category.
- The `_name_map_` dict inside plugins maps aliases to canonical function names.
- Match/group functions return `(result, flag)` tuples where flag controls further processing.

## Development

### Install

```bash
# Install with dev dependencies
python -m pip install poetry
python -m poetry install

# Install with all optional dependencies
python -m poetry install -E full
```

### Run Tests

```bash
cd test/pytest
python -m poetry run pytest -vv
```

Tests are in `test/pytest/`. CI runs tests on Python 3.10–3.14, Windows, with `poetry install -E full`.

### Linting

Uses pre-commit with:
- **black** — code formatting
- **flake8** — style checks
- **pylint** — static analysis (see `pylintrc` for disabled rules)

```bash
python -m poetry run pre-commit run --all-files
```

### Build Docs

```bash
cd docs
make html
```

Docs use Sphinx with ReadTheDocs theme. Source in `docs/source/`.

## Coding Conventions

- **Formatting:** black (line length default)
- **Naming:** snake_case for functions/variables, PascalCase for classes. Internal classes prefixed with `_` and suffixed with `_class` (e.g., `_group_class`).
- **Docstrings:** Sphinx-format (`:param name:`, `:returns:`, `:type:`)
- **pylint config:** Relaxed limits — max-args=50, max-locals=50, max-attributes=50. Disables: line-too-long, broad-except, invalid-name, bare-except, too-many-locals, too-many-arguments.
- **No runtime dependencies.** All imports are optional and loaded lazily. Optional deps: cerberus, jinja2, pyyaml, deepdiff, openpyxl, tabulate, ttp_templates, yangson, n2g.

## CI/CD

GitHub Actions workflow (`.github/workflows/main.yml`):
- **Linters job:** Python 3.10, Windows, runs `pre-commit run --all-files`
- **Tests job:** Python 3.10–3.14, Windows, runs `pytest -vv` from `test/pytest/` with full extras installed

## CLI

TTP provides a CLI tool via the `ttp` entry point:

```bash
ttp --data <data_file> --template <template_file> --outputter <format>
```

Entry point: `ttp.ttp:cli_tool` (defined in `pyproject.toml`).
