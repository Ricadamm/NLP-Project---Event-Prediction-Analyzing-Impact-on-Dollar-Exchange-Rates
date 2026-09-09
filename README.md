# Global Geopolitical Event Prediction: Analyzing Impact on Dollar Exchange Rates

## Project Overview
An end-to-end NLP and analytical pipeline to investigate whether global geopolitical news significantly influences and helps predict fluctuations in the US Dollar (USD) exchange rate.

## Repository Structure
```
├── data/
│   ├── raw/                  # Original BI XLSX + raw GDELT response attempts
│   ├── interim/              # Validated JISDOR and cleaned candidate metadata
│   └── processed/            # Cleaned, aligned final dataset
├── src/
│   ├── scraper_news.py       # GDELT collection CLI wrapper
│   ├── acquisition/          # GDELT client and resumable collector
│   ├── preprocessing/        # JISDOR and news metadata cleaners
│   ├── preprocess_USD-Exchange-Rate.py  # Existing JISDOR CLI, preserved
│   └── data_alignment.py     # Temporal alignment of news and exchange rates
├── config/                  # API settings, sources and human topic taxonomy
├── tests/                   # Offline pytest suite
├── requirements.txt
└── README.md
```

## Task 1: Data Acquisition & Strategic Preprocessing

### Data Sources
- **News Data**: GDELT DOC 2.0 Article List JSON, initially Reuters in English
- **Exchange Rate Data**: Bank Indonesia JISDOR (USD/IDR daily rate, Sep 2021 – Sep 2026)

### Pipeline Steps
1. **Acquisition** — Validate the original BI workbook and collect GDELT candidate metadata through a seven-day pilot before any manual five-year run.
2. **Metadata cleaning** — Normalize URLs, safe title whitespace, and UTC/WIB timestamps; deduplicate while preserving all query categories and provenance.
3. **Later research stages** — Human-justified relevance filtering, model-specific text preparation, and temporal alignment remain future work. The original `data_alignment.py` placeholder is unchanged. Lowercasing, stopword removal and lemmatization are not applied to the Task 1 source titles.

## Setup
```bash
python -m venv .venv
# Activate .venv for your shell, then:
python -m pip install -r requirements.txt
```

## Usage
```bash
# 1. Clean and validate the unchanged BI workbook
python -m src.preprocessing.clean_jisdor

# 2. Collect and clean only the authorized seven-day pilot
python -m src.acquisition.collect_gdelt --start-date 2021-09-01 --end-date 2021-09-07 --pilot

# 3. Run deterministic offline tests
python -m pytest -q
```

## Team Members
- [Member 1]
- [Member 2]
- [Member 3]

## Task 1 data foundation

This implementation extends the existing team repository. The source audit at
`5f812bc` found an implemented `src/preprocess_USD-Exchange-Rate.py`, scraper and
alignment placeholders, the BI workbook, and raw/processed directories. The
README had named a `preprocessing.py` file that was absent. The existing rate
cleaner provided the extraction/parsing/sorting foundation; it now delegates to
the validated module instead of silently dropping invalid or duplicate rows.
No original tracked file was deleted, and the alignment placeholder was not
modified. Existing requirements were retained; only `openpyxl`, `pyyaml`, and
`pytest` were added. Task 1 does not need the NLTK corpus download.

### JISDOR source and validation

Bank Indonesia supplied the original XLSX at
`data/raw/Informasi Kurs Jisdor.xlsx`. It remains at its tracked location rather
than being moved or copied into a new `jisdor/` directory. Its SHA-256 is
`0a8492663f686e4857c33c08923a3c039941c12ae27f03ea31e2227d4ce07c49`.

The inspected workbook has one sheet, `Informasi Kurs Jisdor`, 1,207 sheet rows,
three blank rows, a title row, and `NO`, `Tanggal`, `Kurs` headers on row 5. Its
1,202 actual observations were in descending date order. `Tanggal` contains
month/day/year date strings with time; `Kurs` contains numeric cells. The fourth
column is empty below the title/header area. The output has **exactly**:

```csv
date,jisdor
2021-09-01,14284
2021-09-02,14281
2021-09-03,14261
```

The cleaner discovers a unique XLSX or accepts `--input`, scans sheet contents
for the column names, and extracts by those names rather than fixed positions.
Use `--sheet` for an explicit table if a future workbook has multiple candidate
sheets. It drops `NO`, empty columns, and wholly blank table rows, then parses
dates with pandas and normalizes them to daily resolution. String dates must
include a full ISO or month/day/year calendar date. Numeric Excel serials without
a real date cell and ambiguous/incomplete dates fail instead of being guessed.

Numeric cells are retained; string rates may include `Rp`/`IDR`, whitespace,
thousands separators, or decimal marks according to the policy recorded in QA.
Every observation must have a finite, positive numeric rate. Missing/invalid
values and **all** duplicate dates, including identical duplicates, fail with
source-row diagnostics. No averaging, imputation, scaling, outlier removal,
returns, targets, or synthetic weekend/holiday rows are produced. Missing dates
in QA means null date cells, not gaps in the calendar.

```bash
python -m src.preprocessing.clean_jisdor
# Existing team entry point also works:
python src/preprocess_USD-Exchange-Rate.py
# Explicit alternate source:
python -m src.preprocessing.clean_jisdor --input "data/raw/Informasi Kurs Jisdor.xlsx"
```

Outputs are `data/interim/jisdor/jisdor_clean.csv` and
`data/interim/jisdor/jisdor_cleaning_report.json`. The report calculates row
counts, bounds, nulls, duplicates, numeric dtype, order, parsing policies, and
source/output hashes. Expected values (1,202 rows; 2021-09-01–2026-09-01) are
comparisons only. A failed rerun records `output_valid: false` and removes its
old generated CSV so a stale success cannot be mistaken for current output.
The original XLSX is always read only.

### GDELT collection and reproducibility

`config/gdelt.yaml` controls endpoint, source domains, language, timeouts,
retries, window size, and pacing. `config/geopolitical_topics.yaml` contains the
team's six initial categories unchanged: `armed_conflict`, `sanctions`,
`trade_conflict`, `energy_geopolitics`, `political_instability`, and
`monetary_geoeconomic`. These are transparent **candidate retrieval** choices,
not validated relevance labels. No taxonomy expansion or LLM filtering occurs.

Queries retain configured keyword order, use uppercase `OR`, quote phrases,
and append `domain:reuters.com sourcelang:english` by default. Article List uses
`mode=artlist`, `format=json`, `sort=dateasc`, and `maxrecords=250`. Request
dates use UTC `YYYYMMDDHHMMSS`. Both CLI calendar dates are **inclusive**; the
seven-day pilot means logical `[2021-09-01T00:00:00Z, 2021-09-08T00:00:00Z)`.

Collection starts with daily windows. A response at the configured cap is
potentially truncated, so the window splits into smaller intervals. Midpoints
use minimum-window units, allowing daily trees to reach 15-minute leaves
without zero-duration calls or gaps. Capped terminal intervals retain their
data, log a critical warning, and make QA `collection_complete: false`.

The API documentation does not establish a formal endpoint inclusivity
contract. Each logical interval is padded by one second on both sides; actual
`requested_start`/`requested_end` and unpadded `logical_start`/`logical_end` are
retained in raw provenance. Terminal duplicates are combined by normalized URL.
The integrated collector explicitly counts any records outside the overall
requested UTC period as `excluded_boundary_records` and retains them in raw
files. This convention prevents silent gaps or unreported scope expansion; it
does not establish exhaustive archive coverage.

HTTP 429, 5xx, timeouts and connection errors receive bounded exponential
backoff (default 5, 10, 20, 40, 80 seconds). `Retry-After` is respected; a delay
beyond the configured cap leaves a retryable failure. Permanent client errors
and malformed/non-JSON responses are failures, not empty successes. A valid
`{"articles": []}` is the only successful empty response. A live preflight on
2026-09-09 returned HTTP 429 asking for five seconds between calls. Therefore
the configuration keeps a one-second post-success pause and also enforces at
least five idle seconds after **each response or transport failure** before
starting another attempt. Slow responses therefore do not consume the idle gap.

Each window has an atomic checkpoint under
`data/raw/news/gdelt/_checkpoints/`. Raw JSON attempt files are stored under
`data/raw/news/gdelt/YYYY/YYYY-MM-DD/category/`. They preserve GDELT fields and
query/category, request bounds, logical bounds, and retrieval time. Request
identity includes the query and API configuration, so a changed configuration
does not reuse old state. Status is `pending`, `completed`, `failed`,
`saturated`, or internal `split`. Completed leaf requests are skipped on resume;
failed/pending requests retry; split parents traverse their children. Saturated
leaves remain flagged and are retried only with `--force`, which preserves
earlier numbered raw attempt files. Run only one collector per raw directory
at a time; checkpoint writes are atomic, not a multi-process locking system.

After the configured number of consecutive failed daily jobs (default three),
the collector stops making requests and lists every remaining daily job as
pending. Rerun the same command to retry. Exit codes are `0` for completed
requests without saturated intervals, `2` for incomplete collection, and `1`
for configuration/storage errors. Logs go to `logs/gdelt_collection.log`.
`generated_at_utc` and retrieval timestamps vary between runs; identities,
configuration hashes, query strings, category serialization and data-cleaning
rules are deterministic. Reports include the full configuration snapshot.

```bash
# Pilot; rerun unchanged to resume:
python -m src.acquisition.collect_gdelt --start-date 2021-09-01 --end-date 2021-09-07 --pilot
# Compatibility wrapper:
python src/scraper_news.py --pilot
# Intentionally re-fetch the pilot, preserving earlier raw attempts:
python -m src.acquisition.collect_gdelt --pilot --force
# Narrow diagnostic selection, if the team chooses it:
python -m src.acquisition.collect_gdelt --pilot --topics armed_conflict sanctions --domains reuters.com
```

The **manual full historical command** below is supplied for the team and was
not executed during implementation. Validate live access and pilot QA first.
No arguments without `--pilot` produce a full-range default run.

```bash
python -m src.acquisition.collect_gdelt --start-date 2021-09-01 --end-date 2026-09-01
```

### Candidate cleaning and QA

The collector automatically writes `data/interim/news/gdelt_news_clean.csv`,
`gdelt_news_cleaning_report.json`, `gdelt_news_quarantine.json`, and
`gdelt_pilot_report.json` (`gdelt_collection_report.json` for non-pilot runs).
CSV avoids adding a Parquet dependency. Raw files are never edited by cleaning.

The clean schema retains `article_id`, `original_url`, `normalized_url`,
`title`, `published_at_utc`, `published_at_wib`, `domain`, `language`,
`sourcecountry`, `categories`, `socialimage`, and `retrieved_at_utc`. Additional
columns preserve mobile URLs, original `seendate`, every original URL, source
record counts, quality flags, and the full JSON retrieval provenance.

**Timestamp caveat:** these requested `published_at_*` column names contain
GDELT `seendate`, its first-seen/index time, **not a verified publisher timestamp**.
`timestamp_semantics=gdelt_first_seen` makes this explicit in every row. Parse
as aware UTC, retain UTC, and convert to `Asia/Jakarta` with its explicit offset.
For a repeated URL use its earliest valid first-seen time; preserve other times
in provenance. Later research must evaluate timestamp suitability before
alignment or claims about prediction.

URL cleaning removes only `utm_source`, `utm_medium`, `utm_campaign`,
`utm_term`, and `utm_content`. It preserves the original URL and does not change
path, fragment, ports, remaining parameter order, encoded keys, or article
identity. This conservative exact deduplication may leave URL aliases as
separate articles. IDs are SHA-256 of the normalized URL. Categories are sorted
JSON arrays; overlapping topics, windows and resumed attempts do not erase
membership. Titles receive NFC Unicode and whitespace normalization only;
case, punctuation, numbers and semantic content are preserved.

Invalid/missing URLs are retained in a separate quarantine JSON because they
cannot be assigned a valid URL-based identity. Missing titles and invalid
timestamps on valid URLs stay in the output with flags. No noisy result is
excluded through an undocumented relevance rule.

The QA report includes source/topic scope, terminal raw records, unique URLs,
duplicate occurrences, category/language/domain counts, earliest/latest valid
times, missing URLs/titles, invalid timestamps, HTTP/retry counters, failed
windows, saturated leaves, pending jobs, and boundary exclusions. Saturated
parent responses are raw evidence but do not count as terminal returned
records. Counts reconcile as terminal raw = boundary exclusions + unique
articles + duplicate occurrences + quarantined occurrences. Historic HTTP
counters include selected checkpoint history; `this_run_http` counts only new
network activity. An empty CSV after failure is a schema-bearing artifact,
not proof that there was no news.

Standalone recleaning is also available:

```bash
python -m src.preprocessing.clean_news --input data/raw/news/gdelt
```

Standalone cleaning reads active/latest terminal attempts across its input
directory; it is not scoped to one CLI date selection. Its default outputs are
`gdelt_news_all_candidates.csv`, `gdelt_news_all_candidates_report.json`, and
`gdelt_news_all_candidates_quarantine.json`, keeping the collector's scoped
artifacts and pilot report intact. Use the collector command for study-scoped QA.

QA distinguishes `request_windows_completed`, `unsaturated_retrieval`, and
`timestamp_scope_consistent`; `collection_complete` requires all three. Unexpected
`seendate` bounds are preserved and flagged, including near-boundary values.
The [GDELT metadata documentation](https://blog.gdeltproject.org/new-gkg-2-0-article-metadata-fields/)
describes a 15-minute processing cycle, which may help explain boundary effects,
but it does not establish the exact DOC behavior observed here. No timestamps
are adjusted. A normal resume reuses successful responses and retains their
warnings; use `--force` only when intentionally re-querying after investigating
endpoint behavior.

### Tests and data hygiene

```bash
python -m pytest -q
```

Normal tests use temporary synthetic workbook fixtures and mocked HTTP clients;
they never contact GDELT. They cover extraction, invalid/null/duplicate handling,
sorting, query/phrase syntax, UTC request parameters, 429/5xx/transport retries,
retry exhaustion, JSON validation, window termination, resume/force behavior,
URL identity, category aggregation, timestamp conversion and QA accounting.
There is no live integration test in the default suite. The pilot command is
the explicit live integration run.

The original workbook, compact clean JISDOR CSV, QA, and seven-day pilot raw
evidence can be tracked. Python caches, logs, checkpoint state, and other
historical raw date chunks are ignored. `data/` itself is not ignored. Review
the size of generated outputs before committing any later full collection.

### API and research limitations

The [official 2018 historical-search update](https://blog.gdeltproject.org/doc-2-0-updates-1-5-year-searching-and-updated-mobile-interface/)
describes search from 2017-01-01 onward and an Article List restriction to the
last three months **within a requested window**. Daily 2021 requests follow
that published design. The older rolling-cutoff wording in the
[DOC 2.0 launch documentation](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/)
must not by itself be used to reject the pilot dates. Nevertheless, current
endpoint behavior, historical archive coverage and Reuters availability must
be verified by the live pilot; published capability does not guarantee access.

The endpoint can rate limit or fail, capped minimum windows may omit articles,
and even uncapped responses do not prove complete historical coverage. Query
matches remain candidates and may be unrelated. Article bodies are not fetched
or provided by this pipeline. No body crawler, paywall/anti-bot bypass, relevance
classifier, sentiment model, FinBERT, embeddings, features, train/test split,
returns, interpolation, target creation, or news/JISDOR alignment is performed.
Source selection, taxonomy, relevance validation, timestamp interpretation,
alignment rules, targets and model design remain human research decisions.
