# Verified findings — Operation SKY WATCH 001

**Scope:** SFPD public drone flight-log CSV snapshot; 10,010 rows; SHA-256 `7d93cca64124e26fe53609feb86898249c85804c25d8355874417de78a944a03`.

## Whole dataset

| Year in published flight date | Rows |
|---|---:|
| 2024 (partial) | 325 |
| 2025 | 2,968 |
| 2026 (Jan–Sep only) | 6,717 |
| **Total** | **10,010** |

Dataset-wide blanks, all flight reasons: call type **2,331**; case/event number **1,055**; geocoded location **536**; analysis neighborhood **735**. These are **not** specifically criminal-investigation counts.

## Jan–Sep 2026 criminal-investigation rows

| Measure | Value |
|---|---:|
| Criminal-investigation flight-log rows | 5,619 |
| Rows with blank call type | 447 |
| Share missing a call type | 8.0% |
| Distinct nonblank case/event identifier values | 3,610 |
| Identifiers with all selected call types blank | 240 |
| Identifiers with some blank/some filled | 0 |
| Identifiers with all selected call types filled | 3,370 |

For the 240 all-blank identifiers, **all 240 remained blank** in every associated row of the 10,010-row snapshot. **Seven** identifiers appeared outside the original selection. This is consistent with identifier-associated missing values, but does not reveal the cause.

## Month-by-month values (2026 selected rows)

| Month | Criminal-investigation rows | Blank call types | Rate |
|---|---:|---:|---:|
| Jan | 391 | 35 | 9.0% |
| Feb | 590 | 55 | 9.3% |
| Mar | 567 | 96 | 16.9% |
| Apr | 616 | 38 | 6.2% |
| May | 652 | 56 | 8.6% |
| Jun | 507 | 29 | 5.7% |
| Jul | 620 | 47 | 7.6% |
| Aug | 610 | 29 | 4.8% |
| Sep | 1,066 | 62 | 5.8% |
| **Total** | **5,619** | **447** | **8.0%** |

March had the highest reported blank-call-type rate in this period. Within March there were **96 flagged flight-log rows** associated with **45 distinct identifiers**, and every selected row associated with those identifiers had a blank call type. On March 7, **22** flagged flight-log rows related to **16** identifier values.

## Geographic cross-check — Jan–Sep 2026 criminal-investigation rows

| Published field absent | Among blank-call-type rows (n=447) | Among filled-call-type rows (n=5,172) |
|---|---:|---:|
| `analysis_neighborhood` | 54 (12.1%) | 353 (6.8%) |
| `geocoded_location` | 31 (6.9%) | 220 (4.3%) |
| `location` | 0 (0.0%) | 0 (0.0%) |

The neighborhood and geocode fields were blank at a higher *flight-row* rate when call type was blank. A case/event-level analysis and documentation review are needed before inferring a mechanism.

## Interpretation and limits

**These are records flagged for explanatory review, not findings of legal violations.** Published blanks may arise for many reasons, including privacy considerations, source-data absence, or reporting differences. A flight-log row is not a distinct incident or an exact drone path. The original public data may be amended later, so the digest must accompany published numeric claims.

For filtering and grouping details, see [METHODOLOGY.md](METHODOLOGY.md). Official source: https://data.sf.gov/Public-Safety/San-Francisco-Police-Department-Drone-Flight-Logs/giw5-ttjs
