import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skywatch_audit import parse_date, blank, analyze


class SkywatchTests(unittest.TestCase):
    def test_slash_date(self):
        self.assertEqual(str(parse_date('2026/05/22 12:00:00 AM')), '2026-05-22')

    def test_iso_date(self):
        self.assertEqual(str(parse_date('2025-09-01T07:00:00')), '2025-09-01')

    def test_blank_values(self):
        self.assertTrue(blank(' '))
        self.assertTrue(blank('N/A'))
        self.assertFalse(blank('ASSAULT'))

    def test_year_and_missing_flag(self):
        rows = [dict(date='2026/05/22 12:00:00 AM', reason_for_flight='Criminal Investigation',
                     call_type_original_desc='', case_cad_event_number='example001',
                     flight_duration_minutes='10', analysis_neighborhood='Mission')]
        result = analyze(rows, set(rows[0]))
        self.assertEqual(result['years']['2026'], 1)
        self.assertEqual(result['flags']['criminal_investigation_without_call_type'], 1)


if __name__ == '__main__':
    unittest.main()
