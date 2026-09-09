# Contributing

## Setup

```bash
python -m venv .venv
# Activate .venv for your shell, then:
python -m pip install -r requirements.txt
```

Do not modify `requirements.txt`: its minimum-version policy is deliberately preserved.

## Python 3.11+ required

This code needs **Python 3.11 or newer**. The acquisition step writes UTC
timestamps (`logical_start` / `logical_end`) with a `Z` suffix
(`.isoformat().replace("+00:00", "Z")`), and the cleaning step reads them back
with `datetime.fromisoformat`. `fromisoformat` only accepts a trailing `Z` from
Python 3.11 onward, so on 3.9 or 3.10 the news-cleaning tests in
`tests/test_news_cleaning.py` fail.

This differs from `README.md`, which states "Python 3.10 or newer" and attributes
the requirement to type syntax. Both points are inaccurate: the real floor is
3.11, and the modules use `from __future__ import annotations` rather than
version-specific type syntax. `README.md` is authoritative for project
objectives, but for the interpreter version follow this file.

## Running the pipeline

See `README.md` for the authoritative command reference. In short:

```bash
python -m src.preprocessing.clean_jisdor
python -m src.acquisition.collect_gdelt --start-date 2021-09-01 --end-date 2021-09-07 --pilot
```

A `Makefile` wraps these (`make help` lists the targets). The `pilot` target
contacts the live GDELT API; do not run it casually.

## Running tests

```bash
pytest -q
# or
python -m pytest -q
```

Both invocations work now that `pytest.ini` sets `pythonpath = .`.

## Branches and pull requests

- Branch from the current task branch; use a descriptive name such as
  `task1-<short-topic>` or `fix/<short-topic>`.
- Keep changes scoped; do not bundle unrelated reformatting.
- CI (`.github/workflows/ci.yml`) runs tests on Python 3.11/3.12/3.13, a
  reproducibility check on the clean JISDOR CSV, and `ruff check .`. CI must be
  green before a PR is merged.
- Do not commit `.venv/`, caches, or regenerated files under `data/`.
- Record anything a teammate would need to know in `CHANGELOG.md` under an
  `## Unreleased` heading for your branch: new or changed behaviour, new commands,
  version requirements, and gotchas.

## Scope note

Per `README.md`, human-justified relevance filtering, model-specific text
preparation, and temporal alignment are deferred future work. Do not implement
them without team agreement.
