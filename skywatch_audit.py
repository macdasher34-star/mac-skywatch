#!/usr/bin/env python3
"""MAC BRAIN / SKY WATCH 001 - SFPD published drone flight log audit.

Uses only the Python standard library. Historical transparency data only; not
live flight tracking, access testing or monitoring private drone video feeds.
"""

import argparse
import collections
import csv
import datetime as dt
import hashlib
import html
import json
import pathlib
import sys
import urllib.error
import urllib.request

DATASET = 'giw5-ttjs'
SOURCE_PAGE = 'https://data.sf.gov/Public-Safety/San-Francisco-Police-Department-Drone-Flight-Logs/giw5-ttjs'
EXPORT_URL = 'https://data.sf.gov/api/v3/views/giw5-ttjs/export.csv?accessType=DOWNLOAD'
FALLBACK_URL = 'https://data.sf.gov/resource/giw5-ttjs.csv?%24limit=50000'
EXPECTED = {
    'date', 'case_cad_event_number', 'call_type_original_desc',
    'flight_duration_minutes', 'reason_for_flight', 'location',
    'geocoded_location', 'analysis_neighborhood',
}
BAD_VALUE = {'', 'unknown', 'n/a', 'na', 'null', 'none', 'not available'}


def blank(value):
    return str(value or '').strip().lower() in BAD_VALUE


def parse_date(value):
    value = str(value or '').strip()
    if not value:
        return None
    try:
        return dt.date.fromisoformat(value[:10].replace('/', '-'))
    except ValueError:
        try:
            return dt.datetime.strptime(value[:10], '%m/%d/%Y').date()
        except ValueError:
            return None


def download_to(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    errors = []
    for url in (EXPORT_URL, FALLBACK_URL):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'MAC-BRAIN-Skywatch/1.0 civic-data-audit'})
            with urllib.request.urlopen(req, timeout=60) as response:
                payload = response.read()
            if not payload or b'date' not in payload[:1500].lower():
                raise ValueError('Response did not resemble the expected CSV')
            path.write_bytes(payload)
            return url
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
            errors.append(f'{url}: {exc}')
    raise RuntimeError('Automatic download failed. Download the CSV through the official DataSF page, then use --csv PATH. ' + ' | '.join(errors))


def pct(n, d):
    return f'{100*n/d:.1f}%' if d else 'n/a'


def analyze(rows, columns):
    n = len(rows)
    missing = {col: sum(blank(r.get(col)) for r in rows) for col in EXPECTED}
    years = collections.Counter()
    months = collections.Counter()
    neighborhoods = collections.Counter()
    reasons = collections.Counter()
    flags = collections.Counter()
    flag_by_year = collections.defaultdict(collections.Counter)
    review = []
    odd_duration = []
    invalid_dates = 0
    for row in rows:
        date = parse_date(row.get('date'))
        year = str(date.year) if date else 'undated'
        month = date.strftime('%Y-%m') if date else 'undated'
        years[year] += 1
        months[month] += 1
        if not date:
            invalid_dates += 1
        neighborhood = row.get('analysis_neighborhood') or '(not listed)'
        neighborhoods[neighborhood] += 1
        reason = str(row.get('reason_for_flight') or '').strip()
        reasons[reason or '(blank)'] += 1
        call_type = str(row.get('call_type_original_desc') or '').strip()
        case = str(row.get('case_cad_event_number') or '').strip()
        duration_raw = str(row.get('flight_duration_minutes') or '').strip()
        local_flags = []
        if reason.lower() == 'criminal investigation' and blank(call_type):
            local_flags.append('criminal_investigation_without_call_type')
        if call_type.upper() in {'MISC', 'SURVEILLANCE', 'MISCELLANEOUS'}:
            local_flags.append('vague_call_type')
        if reason.lower() in {'surveillance', 'misc', 'miscellaneous'}:
            local_flags.append('vague_flight_reason')
        if reason.lower() == 'criminal investigation' and (blank(case) or case == '0'):
            local_flags.append('criminal_investigation_without_usable_case_number')
        try:
            duration = float(duration_raw)
            if duration < 0 or duration > 120:
                local_flags.append('duration_outside_0_to_120_minutes_review_threshold')
                odd_duration.append((duration, month, neighborhood))
        except ValueError:
            local_flags.append('invalid_duration')
        for tag in local_flags:
            flags[tag] += 1
            flag_by_year[year][tag] += 1
        if local_flags:
            review.append({
                'date': date.isoformat() if date else '',
                'neighborhood': neighborhood,
                'reason_for_flight': reason,
                'call_type': call_type,
                'flags': '; '.join(local_flags),
            })
    return dict(total=n, columns=sorted(columns), missing=missing, years=dict(sorted(years.items())),
                months=dict(sorted(months.items())), neighborhoods=neighborhoods,
                reasons=reasons, flags=flags, flag_by_year=flag_by_year,
                review=review, odd_duration=sorted(odd_duration, reverse=True),
                invalid_dates=invalid_dates)


def write_csv(path, fields, records):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(records)


def write_reports(out, data, provenance):
    out.mkdir(parents=True, exist_ok=True)
    n = data['total']
    m = data['missing']
    flags = data['flags']
    rows = [
        '# MAC BRAIN — SKY WATCH 001 / Flight Log Audit',
        '',
        f'Generated (UTC): {dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}',
        f'Dataset: {SOURCE_PAGE}',
        f'Source SHA-256: `{provenance["sha256"]}`',
        f'Rows loaded: **{n:,}** (one published flight-log row; not necessarily a distinct police incident)',
        '',
        '## Data quality findings',
        '',
        '| Measure | Count | Share of all flight-log rows |',
        '|---|---:|---:|',
    ]
    for name, label in [
        ('call_type_original_desc', 'Blank call type (all flight categories)'),
        ('case_cad_event_number', 'Blank case / CAD / event number'),
        ('reason_for_flight', 'Blank reason for flight'),
        ('location', 'Blank general location'),
        ('geocoded_location', 'Blank geocoded location'),
        ('analysis_neighborhood', 'Blank analysis neighborhood'),
    ]:
        rows.append(f'| {label} | {m[name]:,} | {pct(m[name], n)} |')
    rows += ['', '### Review flags (NOT findings of unlawful activity)', '',
             '| Flag | Rows |', '|---|---:|']
    for tag, count in sorted(flags.items(), key=lambda x: (-x[1], x[0])):
        rows.append(f'| {tag.replace("_", " ")} | {count:,} |')
    rows += ['', '## Flights by year', '', '| Year | Rows |', '|---|---:|']
    for year, count in data['years'].items():
        rows.append(f'| {year} | {count:,} |')
    rows += ['', '## Most frequently listed analysis neighborhoods', '',
             '| Neighborhood | Rows |', '|---|---:|']
    for area, count in data['neighborhoods'].most_common(12):
        rows.append(f'| {area} | {count:,} |')
    rows += [
        '', '## Important interpretation rules', '',
        '- A missing call type in a training flight is not the same as a missing call type in a criminal investigation.',
        '- Flight records are not unique incidents: multiple drones can serve one CAD event.',
        '- Geographic categories describe published incident/launch context, not confirmed drone flight paths.',
        '- The SFPD changed its reason-for-flight data collection scheme on September 1, 2025; comparisons across that date need caution.',
        '- An unusually long logged duration could be data-entry error, aggregated operation, or a valid entry; investigate rather than assume misconduct.',
        '- The city removes information about juvenile incidents and generalizes locations, so missing location fields are not automatically reporting failures.',
        '- The source is historical public data; this tool does not access live video, private feeds, or individual tracking.',
        '- Source records can be updated later. Verify data freshness before publishing conclusions.',
        '', '## Reproduction', '',
        'Run `python3 skywatch_audit.py --csv PATH_TO_OFFICIAL_CSV` and compare the SHA-256 and generated tables.',
        '',
    ]
    (out/'audit_report.md').write_text('\n'.join(rows), encoding='utf-8')
    write_csv(out/'monthly_flights.csv', ['month','flight_log_rows'],
              [{'month': k, 'flight_log_rows': v} for k, v in data['months'].items()])
    write_csv(out/'review_queue.csv', ['date','neighborhood','reason_for_flight','call_type','flags'], data['review'])
    write_csv(out/'neighborhood_counts.csv', ['analysis_neighborhood','flight_log_rows'],
              [{'analysis_neighborhood': a, 'flight_log_rows': n} for a, n in data['neighborhoods'].most_common()])
    (out/'provenance.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')
    max_month = max(data['months'].values(), default=1)
    monthly = '\n'.join(f'<div class="barrow"><span>{html.escape(month)}</span><div class="track"><div class="bar" style="width:{100*count/max_month:.2f}%"></div></div><strong>{count:,}</strong></div>'
                        for month, count in data['months'].items() if month != 'undated')
    top = '\n'.join(f'<tr><td>{html.escape(area)}</td><td>{count:,}</td></tr>' for area, count in data['neighborhoods'].most_common(12))
    flag_html = '\n'.join(f'<tr><td>{html.escape(k.replace("_", " "))}</td><td>{v:,}</td></tr>' for k,v in flags.most_common())
    page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>MAC BRAIN | SKY WATCH 001</title>
<style>body{{background:#090b10;color:#e8edf4;font:16px system-ui,Arial,sans-serif;max-width:980px;margin:auto;padding:24px;line-height:1.5}}h1{{color:#ef4444;letter-spacing:.04em}}h2{{border-bottom:1px solid #343d4b;padding-bottom:8px;margin-top:34px}}.muted{{color:#aab8ca}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}}.card{{background:#151b26;padding:18px;border:1px solid #2c3543;border-radius:12px}}.num{{font-size:1.9rem;font-weight:750}}.label{{font-size:.86rem;color:#b6c2ce}}table{{border-collapse:collapse;width:100%}}th,td{{padding:9px;border-bottom:1px solid #283241;text-align:left}}td:last-child{{text-align:right}}.barrow{{display:grid;grid-template-columns:90px 1fr 60px;gap:12px;align-items:center;margin:8px 0;font-size:13px}}.track{{background:#272f3e;height:14px;border-radius:5px}}.bar{{background:#c73838;height:100%;border-radius:5px}}a{{color:#f4b466}}small{{color:#aab8ca}}</style>
<h1>MAC BRAIN // SKY WATCH 001</h1><p class="muted">Historical public-data accountability audit · Not a live drone tracker</p>
<div class="cards"><div class="card"><div class="num">{n:,}</div><div class="label">flight-log rows</div></div><div class="card"><div class="num">{m['call_type_original_desc']:,}</div><div class="label">blank call types, all categories</div></div><div class="card"><div class="num">{flags['criminal_investigation_without_call_type']:,}</div><div class="label">criminal-investigation rows with no call type</div></div><div class="card"><div class="num">{m['analysis_neighborhood']:,}</div><div class="label">blank neighborhoods</div></div></div>
<h2>Flights per month</h2>{monthly}
<h2>Review flags — not confirmed violations</h2><table><thead><tr><th>Flag</th><th>Count</th></tr></thead><tbody>{flag_html}</tbody></table>
<h2>Neighborhood counts</h2><p class="muted">Raw counts do not account for population, calls for service, or operational need.</p><table><thead><tr><th>Area</th><th>Rows</th></tr></thead><tbody>{top}</tbody></table>
<p><small>Source: <a href="{SOURCE_PAGE}">DataSF official SFPD drone flight logs</a>. CSV SHA-256: {provenance['sha256']}. Case IDs and exact street locations deliberately omitted from this summary.</small></p></html>'''
    (out/'audit_dashboard.html').write_text(page, encoding='utf-8')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--csv', type=pathlib.Path, help='Path to a previously downloaded official CSV')
    p.add_argument('--out', type=pathlib.Path, default=pathlib.Path('skywatch_output'))
    args = p.parse_args(argv)
    if args.csv:
        source_path = args.csv
        retrieval = 'user-supplied local official dataset CSV (verify provenance independently)'
    else:
        source_path = args.out/'sfpd_drone_flights_original.csv'
        try:
            retrieval = download_to(source_path)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 2
    try:
        with source_path.open('r', newline='', encoding='utf-8-sig') as fh:
            reader = csv.DictReader(fh)
            columns = list(reader.fieldnames or [])
            missing_columns = EXPECTED - set(columns)
            if missing_columns:
                raise ValueError('CSV lacks required DataSF columns: ' + ', '.join(sorted(missing_columns)))
            rows = list(reader)
        if not rows:
            raise ValueError('No flight rows in CSV')
        sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
        provenance = {'dataset_id': DATASET, 'source_page': SOURCE_PAGE,
                      'source_file': str(source_path.resolve()), 'retrieval': retrieval,
                      'sha256': sha, 'rows': len(rows), 'date_processed_utc': dt.datetime.now(dt.timezone.utc).isoformat()}
        data = analyze(rows, columns)
        write_reports(args.out, data, provenance)
        print(f"Processed {data['total']:,} flight rows")
        print(f"Criminal investigations with blank call type: {data['flags']['criminal_investigation_without_call_type']:,}")
        print(f"Dashboard: {(args.out/'audit_dashboard.html').resolve()}")
        print(f"Written audit report: {(args.out/'audit_report.md').resolve()}")
        return 0
    except (OSError, ValueError, csv.Error) as exc:
        print(f'Error reading dataset: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
