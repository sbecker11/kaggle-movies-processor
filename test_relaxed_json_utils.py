from unittest import TestCase

import io
import pandas as pd

from relaxed_json_utils import read_relaxed_json, get_detailed_type

class TestRelaxedJsonUtils(TestCase):
    
    def test_relaxed_json(self):
        test_cases = [
            ('{"key": "value", "number": 4}', "Dict"),
            ('{key: value, number: 40}', "Dict"),
            ('[{name: "John", age: 30}, {"name": Alice, "age": 25}]', "List(dict)"),
            ('44', "int"),
            ('{"name": "le\'Accident", "type": unquoted}', "Dict"),
            ('{complex: "string with \\"internal\\" double quotes"}', "Dict"),
            ('[{name: single\'quote, age: 31}, {"name": "double\\"quote", "age": 25}]', "List(dict)"),
            ('{key: value with spaces, another: 41}', "Dict"),
            ('{"key": "value with spaces", "another": 42}', "Dict"),
            ('{mixed: value with spaces, "quoted": "string with spaces"}', "Dict"),
            ('[{name: John Doe, age: 32}, {"name": "Jane Doe", "job": software engineer}]', "List(dict)"),
            ('This is a naked string', "str"),
            ('true', "bool"),
            ('false', "bool"),
            ('null', "NoneType"),
            ('3.14159', "float"),
            ('["a", "b", "c"]', "List[str]"),
            ('[]', "Empty List"),
            ('{}', "Empty Dict"),
        ]
        num_errors = 0
        json_str_errors = []
        for i, tuple in enumerate(test_cases, 1):
            json_str, expected = tuple
            print(f"Test case {i}: {json_str}, {expected}")
            try:
                result = read_relaxed_json(io.StringIO(json_str))
                detailed_type = get_detailed_type(result)
                if detailed_type != expected:
                    print(f"Expected: {expected} != Got: {detailed_type}")
                    num_errors += 1
                    json_str_errors.append((json_str,expected,detailed_type))
            except Exception as e:
                print(f"Error: {e}")
            print()

        for json_str in json_str_errors:
            print(f"Error found in test_relaxed_json for : {json_str}")
        self.assertEqual(0, num_errors, "Errors found in test_relaxed_json")
    
    
    def test_get_detailed_type(self):
        test_cases = [
            (43, 'int'),
            (3.14159, 'float'),
            ('This is a string', 'str'),
            (True, 'bool'),
            (False, 'bool'),
            (None, 'NoneType'),
            ({'key': 'value'}, 'dict'),
            ([1, 2, 3], 'list'),
            (pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]}), 'DataFrame'),
        ]
        json_str_errors = []
        num_errors = 0
        for i, (obj, expected) in enumerate(test_cases, 1):
            print(f"Test case {i}: {obj}")
            result = get_detailed_type(obj)
            if result != expected:
                num_errors += 1
                print(f"Expected: {expected}, Got: {result}")
                json_str_errors.append((obj, expected, result))
            print()
            
        for json_str in json_str_errors:
            print(f"Error found in test_get_detailed_type for : {json_str}")
        self.assertEqual(0, num_errors, "Errors found in test_get_detailed_type")


    def main(self):
        self.test_relaxed_json()
        self.test_get_detailed_type()
        
if __name__ == '__main__':
    TestRelaxedJsonUtils().main()