import json

# Define the functions to be tested

def is_json_string(val):
    if isinstance(val, str):
        val = val.strip()  # Remove leading/trailing whitespace
        if val.startswith('{') or val.startswith('['):
            try:
                json.loads(val)
                return True
            except (ValueError, TypeError, json.JSONDecodeError):
                return False
    return False

import ast

def is_list_of_tuples(val):
    if isinstance(val, str):
        try:
            # Remove leading and trailing whitespace and any extra spaces
            val = val.strip()
            # Safely evaluate the string to a Python object
            parsed_val = ast.literal_eval(val)
            # Check if the result is a list
            if isinstance(parsed_val, list):
                # Determine the expected length of tuples (if any)
                expected_length = None
                for item in parsed_val:
                    # Ensure every element is a tuple with at least two elements
                    if not isinstance(item, tuple) or len(item) < 2:
                        return False
                    # Set the expected length based on the first tuple
                    if expected_length is None:
                        expected_length = len(item)
                    # Ensure all tuples have the same length
                    if len(item) != expected_length:
                        return False
                    # Check that all elements in the tuple are of allowed types
                    if not all(isinstance(elem, (int, float, str, bool, type(None), tuple)) for elem in item):
                        return False
                return True
        except (ValueError, SyntaxError):
            # Return False if the string cannot be parsed to a Python object
            return False
    return False


# Define test cases for the functions

import unittest

class TestDataFunctions(unittest.TestCase):

    def test_is_json_string(self):
        test_cases = [
            # Valid JSON strings
            ('{"key": "value"}', True),
            ('{"number": 123, "boolean": true}', True),
            ('[]', True),
            ('{}', True),
            
            # Invalid JSON strings
            ('{key: "value"}', False),
            ('{number: 123, boolean: true', False),
            ('[unclosed bracket', False),
            ('{key: "value", }', False),

            # Non-JSON strings
            ('Hello, World!', False),
            ('123', False),
            ('True', False)
        ]

        for input_str, expected in test_cases:
            with self.subTest(input_str=input_str):
                self.assertEqual(is_json_string(input_str), expected)

    def test_is_list_of_tuples(self):
        test_cases = [
            # Valid list of tuples
            ('[("a", 1), ("b", 2)]', True),
            ('[("x", "y"), (1, 2)]', True),
            ('[((1, 2), (3, 4)), ((5, 6), (7, 8))]', True),  # Nested tuples
            ('[("a", 1, True), ("b", None, 3.5)]', True),

            # Additional test cases for better coverage
            ('[ ("a", 1) , ("b" ,2) ]', True),  # Whitespace handling
            ('[("a, b", 1), ("c\'s", 2)]', True),  # Special characters in strings
            ('[((1, (2, 3)), 4), ((5, (6, 7)), 8)]', True),  # Complex nested tuples

            # Edge cases
            ('[]', True),  # Empty list
            ('[()]', False),  # List with an empty tuple
            ('[(1,)]', False),  # List with a single-element tuple
            ('[("a",)]', False),  # List with a single-element tuple

            # Invalid list of tuples
            ('[("a", 1), "b", 2]', False),  # Mixed types, not all tuples
            ('[("a", 1), (2,)]', False),  # Tuple with only one element
            ('[("a", 1), (2, "b", 3)]', False),  # Tuples with different lengths
            ('("a", 1), ("b", 2)', False),  # Missing square brackets around the list
            ('123', False),  # Not a list

            # Non-list of tuples strings
            ('Hello, World!', False),
            ('True', False),
            ('[1, 2, 3]', False)  # List of integers, not tuples
        ]

        for input_str, expected in test_cases:
            with self.subTest(input_str=input_str):
                self.assertEqual(is_list_of_tuples(input_str), expected)

# Run the tests
if __name__ == '__main__':
    unittest.main()
