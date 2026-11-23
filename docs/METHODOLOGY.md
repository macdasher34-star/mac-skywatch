# Methodology and reproducibility — SKY WATCH 001

## Question

How complete and internally consistent are the *public* SFPD drone flight-log records, particularly their `call_type_original_desc` field for flights recorded as `Criminal Investigation`?

## Source and snapshot

- Dataset: [San Francisco Police Department Drone Flight Logs](https://data.sf.gov/Public-Safety/San-Francisco-Police-Department-Drone-Flight-Logs/giw5-ttjs), DataSF identifier `giw5-ttjs`.
- Local audit report generated in UTC on **2026-11-23** for the user's downloaded dataset. Date field coverage from 2024 through **September 30, 2026**; September 2026 is the last included flight month in this snapshot.
- Raw CSV integrity digest: `7d93cca64124e26fe53609feb86898249c85804c25d8355874417de78a944a03`.
- 10,010 **rows**: one published flight-log entry per row; multiple entries can share one dispatch case/event identifier.

Counts in this document come from local terminal outputs for the snapshot above, not from a fresh independent download of the complete CSV in this packaged environment.

## Field definitions

- `date`: local calendar date parsed from values such as `2026/05/22 12:00:00 AM`. The first ten characters are converted from `YYYY/MM/DD` to `YYYY-MM-DD`; ISO-like strings are also supported.
- `reason_for_flight`: rows are classified as criminal investigations when stripped, lowercased text equals `criminal investigation`.
- `call_type_original_desc`: treated as blank if empty/whitespace or one of the existing script's `BAD_VALUE` placeholders (`unknown`, `n/a`, etc.).
- `case_cad_event_number`: compared as **string identifiers**, not guaranteed unique incident IDs.
- `analysis_neighborhood` and `geocoded_location`: compared as published fields, not direct flight tracks.

## Scoped calculations

1. Read official CSV with `csv.DictReader(encoding='utf-8-sig')` and preserve the raw source file.
2. Parse `date`; retain dates in **Jan 1–Sep 30, 2026**, inclusive. Filter `reason_for_flight == 'criminal investigation'` case-insensitively.
3. Count row-level blank `call_type_original_desc` entries: **447 / 5,619 = 8.0%** (rounded to one decimal place).
4. Group selected records by nonblank `case_cad_event_number`: **3,610 distinct identifier values**.
5. Classify each identifier as **all blank** (every selected row has blank call type), **mixed** (some blank/some filled), or **all filled**. Output: **240 / 0 / 3,370**.
6. Collect the 240 flagged identifiers, then search the **full 10,010-row snapshot** across dates and reasons: all **240** remained blank in every matching row; **7** appeared in one or more rows outside the 2026 criminal-investigation selection.
7. For March 2026 separately: **567** criminal-investigation rows, **96** with blank call types; **353** distinct nonblank identifiers, of which **45** were all blank and **0** mixed.

## Data-quality caveats

- Even if all rows for one case/event identifier have blank call types, this does **not** identify *where* the missingness originated (dispatch, normalization, publication policy, or another process).
- No assertion can be made here about the legality or purpose of any individual flight. We did **not** view footage or access private systems.
- There are no mixed identifiers among the filtered selected records; this does **not** imply all fields are complete or that identifiers always map one-to-one to incidents.
- Neighborhood group totals, especially small groups, are descriptive. The analysis did not adjust for population, calls-for-service, or operational factors.
- City data may change over time; compare **SHA-256 digest and dates** before asserting exact reproduction.
- Duration values outside 0–120 minutes are code-defined review thresholds only, not official legal limits.
- The source script initially misread slash-formatted dates and classified all rows as undated. That problem was fixed by normalizing slashes to hyphens in `parse_date`, then verified with a sample date and corrected annual counts.

## Reproduce

```bash
python3 -m unittest discover -s tests -v
python3 skywatch_audit.py --csv /path/to/official.csv
sha256sum /path/to/official.csv
```

The standard script produces whole-dataset audit tables and a dashboard. **The 2026 identifier-group analysis was performed using additional read-only terminal scripts** and is reported in [FINDINGS.md](FINDINGS.md); those figures are not automatically generated as separate dashboard cards by the standard script yet. This distinction is essential when describing reproducibility.

## Disclosure and publication

Publish summary statistics, algorithm and criteria, source URLs, dates, and checksums. Avoid publishing case numbers, sensitive incident descriptions, personal information, private footage, local workstation paths, or unreviewed raw exports.
