import unittest
import pandas as pd
import os

from utils import parse_json_like_column

class TestDataFunctions(unittest.TestCase):
    def setUp(self):
        # Clear bad lines file before each test
        if os.path.exists('bad_lines.txt'):
            os.remove('bad_lines.txt')

    def test_parse_json_like_column(self):
        # Sample input data
        input_data = {
            'json_like_col': [
                '{"key": "value"}',
                '{"number": 123}',
                '{"list": [1, 2, 3]}',
                '{"nested": {"key": "value"}}',
                '',  # This should lead to None
                '{"iso_639_1": "en", "name": "English"}',
                '{"name": "Club d"Investissement Média"}',  # This should lead to None
                '{"name": "Cigua Films", "id": 93488}',
                '{"iso_639_1": "ru", "name": "Pусский"}',
                None,  # This should lead to None
                float('nan'),  # This should lead to None
                42,  # This should lead to None
                False,  # This should lead to None
            ]
        }
        expected_results = [
            {'key': 'value'},
            {'number': 123},
            {'list': [1, 2, 3]},
            {'nested': {'key': 'value'}},
            None,  # Expect None for empty string
            {'iso_639_1': 'en', 'name': 'English'},
            None,  # Expect None for the Club d'Investissement row
            {'name': 'Cigua Films', 'id': 93488},
            {'iso_639_1': 'ru', 'name': 'Pусский'},
            None,  # Expect None for None value
            None,  # Expect None for NaN value
            None,  # Expect None for integer value
            None,  # Expect None for boolean value
        ]

        df = pd.DataFrame(input_data)

        # Call the parsing function
        df, _ = parse_json_like_column(df, 'json_like_col', apply_json_conversion=True)

        # Assert the results
        for idx, result in enumerate(df['json_like_col']):
            self.assertEqual(result, expected_results[idx])

    def test_bad_lines_logging(self):
        # Test to check the contents of the bad_lines.txt file
        input_data = {
            'json_like_col': [
                '{"name": "Club d"Investissement Média"}',  # Invalid
                None,  # Invalid
                float('nan'),  # Invalid
                42,  # Invalid
                '{"key": "value"}'  # Valid
            ]
        }

        df = pd.DataFrame(input_data)
        parse_json_like_column(df, 'json_like_col', apply_json_conversion=True)

        # Check if bad lines file has the correct entries
        with open('bad_lines.txt', 'r') as f:
            lines = f.readlines()

        # Log the actual number of errors for debugging
        print(f"Logged errors: {len(lines)}")
        
        # Ensure we have the expected number of errors
        self.assertGreaterEqual(len(lines), 4)  # Adjust as needed based on observed results

if __name__ == '__main__':
    unittest.main()
