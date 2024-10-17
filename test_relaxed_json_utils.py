from unittest import TestCase

import io
import pandas as pd

from relaxed_json_utils import read_relaxed_json, get_detailed_type

class TestRelaxedJsonUtils(TestCase):
    
    def test_relaxed_json(sel):
        test_cases = [
            '{"key": "value", "number": 42}',
            '{key: value, number: 42}',
            '[{name: "John", age: 30}, {"name": Alice, "age": 25}]',
            '42',
            '{"name": "le\'Accident", "type": unquoted}',
            '{complex: "string with \\"internal\\" double quotes"}',
            '[{name: single\'quote, age: 30}, {"name": "double\\"quote", "age": 25}]',
            '{key: value with spaces, another: 42}',
            '{"key": "value with spaces", "another": 42}',
            '{mixed: value with spaces, "quoted": "string with spaces"}',
            '[{name: John Doe, age: 30}, {"name": "Jane Doe", "job": software engineer}]',
            'This is a naked string',
            'true',
            'false',
            'null',
            '3.14159',
            '["a", "b", "c"]',
            '[]',
            '{}',
        ]

        for i, json_str in enumerate(test_cases, 1):
            print(f"Test case {i}: {json_str}")
            try:
                result = read_relaxed_json(io.StringIO(json_str))
                detailed_type = get_detailed_type(result)
                print(f"Parsed type: {detailed_type}")
                print(f"Result: {result}")
            except Exception as e:
                print(f"Error: {e}")
            print()
    
    def test_get_detailed_type(self):
        test_cases = [
            (42, 'int'),
            (3.14159, 'float'),
            ('This is a string', 'str'),
            (True, 'bool'),
            (False, 'bool'),
            (None, 'NoneType'),
            ({'key': 'value'}, 'dict'),
            ([1, 2, 3], 'list'),
            (pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]}), 'DataFrame'),
        ]

        for i, (obj, expected) in enumerate(test_cases, 1):
            print(f"Test case {i}: {obj}")
            result = get_detailed_type(obj)
            print(f"Expected: {expected}, Got: {result}")
            print()

    def main(self):
        self.test_relaxed_json()
        self.test_get_detailed_type()
        
if __name__ == '__main__':
    TestRelaxedJsonUtils().main()