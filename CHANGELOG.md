# Changelog

All notable changes to this project are recorded here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The project does not
publish versioned releases, so entries are grouped by the branch or pull request
that introduced them.

## Unreleased — `task1-ci-and-developer-tooling`

Infrastructure and quality only. No change to acquisition logic, cleaning rules,
the taxonomy, tracked data, or `README.md` objectives. `data_alignment.py`
remains the untouched placeholder the README describes.

### Added

- **Continuous integration** (`.github/workflows/ci.yml`). Runs on every push and
  on pull requests into `main`:
  - `test` — the full offline pytest suite on Python 3.11, 3.12, and 3.13.
  - `reproducibility` — regenerates `data/interim/jisdor/jisdor_clean.csv` from
    the tracked Bank Indonesia workbook and fails if it is not byte-identical.
    Only the CSV is checked; `jisdor_cleaning_report.json` embeds
    `generated_at_utc` and is expected to differ.
  - `lint` — `ruff check .`.
- **`Makefile`** with self-documenting targets that wrap the commands the README
  already documents: `make setup`, `test`, `lint`, `jisdor`, `pilot`,
  `report-only`, `clean`. Run `make help` for the list. `PYTHON ?= python` lets
  you point every target at a virtualenv, e.g. `make PYTHON=.venv/bin/python test`.
- **`pyproject.toml`** — ruff configuration only (no packaging metadata). Line
  length is not enforced; the existing modules predate any formatter.
- **`CONTRIBUTING.md`**, **`.github/pull_request_template.md`**, **`.editorconfig`**.
- **`CHANGELOG.md`** (this file).

### Changed

- `pytest.ini` sets `pythonpath = .` so a bare `pytest` works from the repository
  root. Previously only `python -m pytest` succeeded; a plain `pytest` failed
  collection with `ModuleNotFoundError: No module named 'src'`.
- `src/preprocessing/clean_news.py` pins the cleaned `published_at_utc` /
  `published_at_wib` columns to nanosecond resolution with `.dt.as_unit("ns")`.
  A fresh `pip install -r requirements.txt` now resolves **pandas 3**, and on
  pandas 3 `pd.to_datetime` infers second resolution for an empty frame, which
  broke the documented `datetime64[ns, UTC]` output schema. Behaviour on
  pandas 2.2.3 (the version the README records) is unchanged. No test or expected
  output was modified.
- `.gitignore` ignores `.ruff_cache/`.

### Notes for contributors

- **Use Python 3.11 or newer.** `README.md` currently says "Python 3.10 or
  newer"; that is too low. `src/acquisition/collect_gdelt.py` writes timestamps
  with a trailing `Z`, and `src/preprocessing/clean_news.py` reads them back with
  `datetime.fromisoformat`, which only accepts a trailing `Z` from Python 3.11.
  On 3.9 or 3.10, eight tests in `tests/test_news_cleaning.py` fail for this
  reason alone. See `CONTRIBUTING.md`.
- **`requirements.txt` is intentionally unpinned** (`pandas>=2.0.0`, etc.), per
  the policy the README states. The pandas 3 fix above addresses the current
  break, but the next major release of any dependency can surface a similar one.
  CI on the matrix above is what will catch it early.
- Run `make lint` (or `ruff check .`) before opening a pull request; CI enforces it.
