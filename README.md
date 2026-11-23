
# MAC DEFENSE SYSTEMS | Operation SKY WATCH 001

**Historical civic-data audit · Python · Linux · Data quality · Reproducible research**

**[View the public SKY WATCH dashboard](https://macdasher34-star.github.io/mac-skywatch/)** · **[Official DataSF source](https://data.sf.gov/Public-Safety/San-Francisco-Police-Department-Drone-Flight-Logs/giw5-ttjs)**

SKY WATCH is an independent, read-only analysis of **San Francisco Police Department public drone-flight logs**. It investigates missing fields, reporting consistency, and differences between flight-level and case/event-identifier-level counts. It does **not** track live drones or access any police systems, private video, or personal accounts.

## Key findings from the recorded snapshot

| Measure | Result |
|---|---:|
| Published flight-log rows examined (May 2024–Sep 2026) | **10,010** |
| Jan–Sep 2026 flight-log rows | **6,717** |
| Jan–Sep 2026 criminal-investigation rows | **5,619** |
| Criminal-investigation rows in that period with blank call type | **447 (8.0%)** |
| Distinct case/event identifier values among selected rows | **3,610** |
| Identifier values where **every** selected call type was blank | **240** |
| Identifier values containing both blank and filled call types | **0** |

The 240 flagged identifiers were also checked against the entire downloaded dataset: **none had a filled call type in any associated row**. These are data-quality patterns, **not allegations of misconduct**. One identifier is not necessarily one distinct incident; a flight-log row is not a flight path.

Full results: [docs/FINDINGS.md](docs/FINDINGS.md). Definition, limitations, snapshot fingerprint, and methods: [docs/METHODOLOGY.md](docs/METHODOLOGY.md).

## What the project demonstrates

- Python standard-library CSV processing, data validation, filtering, aggregation, and HTML report generation.
- Linux command-line workflows, troubleshooting a real date-format parsing defect, and verification with automated tests.
- SHA-256 dataset integrity checks and reproducible, scoped results.
- Responsible interpretation of public records and privacy-preserving summary publication.

## Run the audit locally

Requires **Python 3**; no third-party packages and no accounts or API tokens. Use only the public historical records you are authorized to retrieve.

```bash
python3 skywatch_audit.py --help
python3 skywatch_audit.py --csv /path/to/official-export.csv
```

Alternatively, `python3 skywatch_audit.py` attempts to download the official public CSV. Output is written to `skywatch_output/` and includes `audit_dashboard.html`, `audit_report.md`, `monthly_flights.csv`, `review_queue.csv`, `neighborhood_counts.csv`, and `provenance.json`.

Check the date parser using a synthetic example and run local tests:

```bash
python3 -m unittest discover -s tests -v
python3 skywatch_audit.py --csv sample/sample_synthetic_only.csv --out /tmp/skywatch-demo
```

**Note:** `sample/sample_synthetic_only.csv` is synthetic test data. It is **not** the official SFPD dataset and its sample output must not be presented as real results.

## Source integrity

SHA-256 of the **10,010-row official CSV snapshot analyzed locally**:

```text
7d93cca64124e26fe53609feb86898249c85804c25d8355874417de78a944a03
```

For a matching local CSV, run `sha256sum /path/to/official-export.csv`. Public source data may be updated; later snapshots can yield different counts. Source dataset ID: `giw5-ttjs`.

## Ethics, limitations and project status

- Missing or vague fields are **review flags**, not proof of illegal surveillance, deliberate redaction, or policy noncompliance.
- We cannot determine why a given call-type value is blank from the published log alone. Privacy treatment, source systems, and reporting workflows require additional evidence.
- Neighborhood values are generalized record context; do not interpret them as exact drone paths or measured surveillance exposure.
- The public dashboard is a **static snapshot**, not a live connected database.
- Public repo should exclude raw case-level data, local paths, credentials, and any account information. This repo's HTML summary intentionally presents aggregate counts.

## Project structure

```text
index.html                 # Existing published GitHub Pages dashboard (keep your current copy)
README.md                  # This page
skywatch_audit.py          # Python audit code (slash-date fix included)
docs/FINDINGS.md           # Independently reproduced results
docs/METHODOLOGY.md      # Data and calculation method
docs/PORTFOLIO.md        # Employer-facing project description
sample/sample_synthetic_only.csv
tests/test_skywatch.py
.gitignore
```

## Sources and acknowledgment

- [SFPD Drone Flight Logs — DataSF](https://data.sf.gov/Public-Safety/San-Francisco-Police-Department-Drone-Flight-Logs/giw5-ttjs)
- [DataSF dataset column metadata](https://data.sf.gov/api/views/giw5-ttjs/columns.json)
- [San Francisco Public Press investigation, Nov 2026](https://www.sfpublicpress.org/police-drone-data-reveals-lack-of-transparency-privacy-concerns/)

Independent educational analysis by **MAC DEFENSE SYSTEMS**. Not affiliated with SFPD, DataSF, or the news publisher.
