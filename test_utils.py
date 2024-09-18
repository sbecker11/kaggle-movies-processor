import unittest
import pandas as pd
from utils import parse_json_or_json_like_column, parse_list_of_tuples_column

class TestDataFunctions(unittest.TestCase):

    def test_parse_json_column(self):
        """
        Test parsing proper JSON columns.
        """
        data = {
            'json_col': [
                '{"key": "value"}',  # Valid JSON
                '{"number": 123}',  # Valid JSON with a number
                '{"list": [1, 2, 3]}',  # Valid JSON with a list
                '{"nested": {"key": "value"}}',  # Valid JSON with a nested object
                'invalid json',  # Invalid JSON string
                '42',  # Not JSON
            ]
        }
        df = pd.DataFrame(data)

        # Parse the JSON column
        df = parse_json_or_json_like_column(df, 'json_col', apply_json_conversion=False)

        # Expected results after parsing
        expected_results = [
            {'key': 'value'},
            {'number': 123},
            {'list': [1, 2, 3]},
            {'nested': {'key': 'value'}},
            None,  # Invalid JSON
            None  # Not JSON
        ]

        for idx, result in enumerate(df['json_col']):
            with self.subTest(idx=idx):
                self.assertEqual(result, expected_results[idx])

    def test_parse_json_like_column(self):
        """
        Test parsing JSON-like columns (with single quotes instead of double quotes).
        """
        data = {
            'json_like_col': [
                "{'key': 'value'}",  # JSON-like
                "{'number': 123}",  # JSON-like with a number
                "{'list': [1, 2, 3]}",  # JSON-like with a list
                "{'nested': {'key': 'value'}}",  # JSON-like with a nested object
                'invalid json',  # Invalid JSON string
                '42',  # Not JSON
            ]
        }
        df = pd.DataFrame(data)

        # Parse the JSON-like column (apply conversion)
        df = parse_json_or_json_like_column(df, 'json_like_col', apply_json_conversion=True)

        # Expected results after parsing
        expected_results = [
            {'key': 'value'},
            {'number': 123},
            {'list': [1, 2, 3]},
            {'nested': {'key': 'value'}},
            None,  # Invalid JSON
            None  # Not JSON
        ]

        for idx, result in enumerate(df['json_like_col']):
            with self.subTest(idx=idx):
                self.assertEqual(result, expected_results[idx])

    def test_parse_list_of_tuples_column(self):
        """
        Test parsing list of tuples columns.
        """
        data = {
            'tuple_col': [
                '[("a", 1), ("b", 2)]',  # List of tuples
                '[("x", "y"), (1, 2)]',  # List of tuples with mixed types
                'invalid tuple list',  # Invalid tuple string
                '[("a",)]'  # List with single-element tuple (invalid for our use case)
            ]
        }
        df = pd.DataFrame(data)

        # Parse the list of tuples column
        df = parse_list_of_tuples_column(df, 'tuple_col')

        # Expected results after parsing
        expected_results = [
            [('a', 1), ('b', 2)],
            [('x', 'y'), (1, 2)],
            None,  # Invalid tuple string
            None  # Single-element tuple, which we're considering invalid
        ]

        for idx, result in enumerate(df['tuple_col']):
            with self.subTest(idx=idx):
                self.assertEqual(result, expected_results[idx])

# Run the tests
if __name__ == '__main__':
    unittest.main()
