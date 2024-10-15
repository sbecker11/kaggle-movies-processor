from column_types import extract_dict, extract_object, extract_string, extract_integer, extract_float, extract_boolean, extract_list_of_dict, extract_ymd_datetime, cast_to_string, cast_to_boolean, cast_to_float, cast_to_integer, process_columns, verify_all_columns_have_extractors
from unittest import TestCase
import pandas as pd

class TestColumnTypes(TestCase):

    def test_extract_string(self):
        s = "[{'id': 16, 'name': 'Animation2'}]"
        x = extract_string(s)
        self.assertEqual(x, s, "Error should be equal")
        
        s = "  [{'id': 16, 'name': 'le'Animation3'}]  "
        expected = "[{'id': 16, 'name': 'le'Animation3'}]"
        x = extract_string(s)
        self.assertEqual(x, expected, f"Error should match expected stripped version of s {expected}")

    def test_extract_dict(self):
        s = "{'id': 16, 'name': 'Animation5'}"
        x = extract_dict(s)
        self.assertIsNotNone(x, "Error should not have returned None")
        self.assertIsInstance(x, dict, "Error should have returned a dict")

        s = "{'id': 16, 'name': 'le\\'Animation6'}"
        x = extract_dict(s)
        self.assertIsNotNone(x, "Error should not have returned None")
        self.assertIsInstance(x, dict, "Error should have returned a dict")

    def test_extract_integer(self):
        x = "123"
        y = extract_integer(x)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, int, "Error should have returned an integer")
        self.assertEqual(y, 123, "Error should have returned 123")
        
        x = "123.14"
        y = extract_integer(x)
        self.assertIsNone(y, "Error should have returned None")
        
        x = "123E-10"
        y = extract_integer(x)
        self.assertIsNone(y, "Error should have returned None")
        
        x = "  "
        y = extract_integer(x)
        self.assertIsNone(y, "Error should have returned None")
        
        x = "123.00000"
        y = extract_integer(x)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, int, "Error should have returned an integer")
        self.assertEqual(y, 123, "Error should have returned 123")

    def test_extract_float(self):
        x = "3.14"
        y = extract_float(x)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, float, "Error should have returned a float")
        self.assertEqual(y, 3.14, "Error should have returned 3.14")

        x = "3.14.14"
        y = extract_float(x)
        self.assertIsNone(y, "Error should have returned None")

        x = "3.14E-10"
        y = extract_float(x)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, float, "Error should have returned a float")
        
        x = 8.387519
        y = extract_float(x)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, float, "Error should have returned a float")
        self.assertEqual(y, x, f"Error should have returned {x}")

    def test_extract_boolean(self):
        x = "True"
        y = extract_boolean(x)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, bool, "Error should have returned a boolean")
        self.assertEqual(y, True, "Error should have returned True") 

        x = "False"
        y = extract_boolean(x)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, bool, "Error should have returned a boolean")
        self.assertEqual(y, False, "Error should have returned False") 

        x = "Falsee"
        y = extract_boolean(x)
        self.assertIsNone(y, "Error should have returned None")

        x = None
        y = extract_boolean(x)
        self.assertIsNone(y, "Error should have returned None")

        x = "  "
        y = extract_boolean(x)
        self.assertIsNone(y, "Error should have returned None")
    
    def test_extract_object(self):
        case_a = "[{'id': 16, 'name': 'le'Animation1'}, {'id': 17, 'name': 'Action'}]"
        result_a = extract_object(case_a)
        self.assertIsNotNone(result_a, "Error result should not be None")
        self.assertIsInstance(result_a, list)
        
        case_b = None
        result_b = extract_object(case_b)
        self.assertIsNone(result_b, "Error result should be None")

    def test_extract_list_of_dict(self):
        "{'id': 10194, 'name': 'Toy Story Collection', 'poster_path': '/7G9915LfUQ2lVfwMEEhDsn3kT4B.jpg', 'backdrop_path': '/9FBwqcd9IRruEDUrTdcaafOMKUq.jpg'}"
        '[{\'name\': \'The Booking Office\', \'id\': 12909}, {\'name\': "Workin\' Man Films", \'id\': 12910}]'
        '[{\'name\': "Po\' Boy Productions", \'id\': 11787}]'
        '[{\'name\': \'Canal+\', \'id\': 5358}, {\'name\': \'Zespól Filmowy "Tor"\', \'id\': 7984}, {\'name\': \'Norsk Film\', \'id\': 12984}, {\'name\': \'Sidéral Productions\', \'id\': 63751}]'
        '[{\'name\': \'Hemdale\', \'id\': 16593}, {\'name\': "Cinema \'84/Greenberg Brothers Partnership", \'id\': 84526}]'
        
        case_a =     "[{'id': 16, 'name': 'le'Animation1'}, {'id': 17, 'name': 'Action'}]"
        expected_a =  [{'id': 16, 'name': 'le\'Animation1'}, {'id': 17, 'name': 'Action'}]
        result_a = extract_list_of_dict(case_a)
        self.assertIsNotNone(result_a, "Error result should not be None")
        self.assertEqual(expected_a, result_a, f"expected {expected_a} but got {result_a}")

        x = "[{'id': 16, 'name': 'AnimationA'}, {'id': 35, 'name': 'Comedy'}, {'id': 10751, 'name': 'Family'}]"
        expected = [{'id': 16, 'name': 'AnimationA'}, {'id': 35, 'name': 'Comedy'}, {'id': 10751, 'name': 'Family'}]
        y = extract_list_of_dict(x)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, list, "Error should have returned a list")
        self.assertEqual(y, expected, f"Error should have returned {expected}")
                
        x = "[{'id': 16, 'name': 'AnimationB'}, [1,2], 3]"
        y = extract_list_of_dict(x)
        self.assertIsNone(y, "Error should have returned None because list it contains non-dicts")
        
        x = "[]"
        y = extract_list_of_dict(x)
        self.assertIsNone(y, "Error should have returned None since string has zero dicts")
                
        x = [{"name": "Yermoliev", "id": 88753}]
        y = extract_list_of_dict(x)
        self.assertIsNone(y, "Error should have returned None since x is not a string")

        x = '[{}]'
        y = extract_list_of_dict(x)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, list, "Error should have returned a list")
        self.assertTrue(len(y) == 1, "Error should have returned a list of length 1")
        
        x = "[{}]"
        y = extract_list_of_dict(x)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, list, "Error should have returned a list")
        self.assertTrue(len(y) == 1, "Error should have returned a list of length 1")

    def test_extract_ymd_datetime(self):
        x = "2022-10-11"
        y = extract_ymd_datetime(x)
        expected = pd.to_datetime("2022-10-11", format="%Y-%m-%d")
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertEqual(y, expected, f"Error should have returned {expected}")
        
        x = "2022-10-1"
        y = extract_ymd_datetime(x)
        self.assertIsNone(y, "Error should have returned None since length != 10 chars")
        
        x = "2022-10-11T14:14:14.123=06:00"
        y = extract_ymd_datetime(x)
        self.assertIsNone(y, "Error should have returned None since length != 10 chars")

    def test_cast_all_values_to_float(self):
        input_data = {
            'A': ['1', '2', 'a'],
            'B': ['4.5', True, 'b'],
            'C': ['7', 'false', 'c']
        }
        expected_data = {
            'A': [1.0, 2.0, None],
            'B': [4.5, None, None],
            'C': [7.0, None, None]
        }
        error_message = self.print_and_compare("make all values float", input_data, expected_data, cast_to_float)
        if error_message:
            self.fail(error_message)
    
    def test_cast_all_values_to_boolean(self):
        input_data = {
            'A': ['true', 'FALSE', 'a'],
            'B': ['4.5', '5.6', True],
            'C': ['7', '8', False]
        }
        expected_data = {
            'A': [True, False, None],
            'B': [None, None, True],
            'C': [None, None, False]
        }
        error_message = self.print_and_compare("test_cast_all_values_to_booleans", input_data, expected_data, cast_to_boolean)
        if error_message:
            self.fail(error_message)

    def test_cast_all_values_to_integer(self):
        input_data = {
            'A': ['1', '2', 'a'],
            'B': ['4.5', True, 'b'],
            'C': ['7', '8', 'c']
        }
        expected_data = {
            'A': [1, 2, None],
            'B': [5, None, None],
            'C': [7, 8, None]
        }
        error_message = self.print_and_compare("test_cast_all_values_to_integers", input_data, expected_data, cast_to_integer)
        if error_message:
            self.fail(error_message)
            
    def test_cast_all_values_to_string(self):
        input_data = {
            'A': [1, '2', '{"a": 7}' ],
            'B': ['happy', 'day\s', '[{"b": 8},{"c": 9}]' ],
            'C': [7, True, '(1,2,3)']
        }
        expected_data = {
            'A': ['1', '2', '{"a": 7}' ],
            'B': ['happy', 'day\s', '[{"b": 8},{"c": 9}]' ],
            'C': ['7', 'True', '(1,2,3)']
        }
        error_message = self.print_and_compare("test_cast_all_values_to_strings", input_data, expected_data, cast_to_string)
        if error_message:
            self.fail(error_message)

    def print_and_compare(self, test_name, input_data, expected_data, converter):
        print('-' * 80)
        print(test_name)
        df_input = pd.DataFrame(input_data)
        print("df_input:")
        print(df_input)
        df_result = df_input.map(converter)
        print("df_result:")
        print(df_result)
        df_expected = pd.DataFrame(expected_data)
        print("df_expected:")
        print(df_expected)
        result = df_result.equals(df_expected)
        if result is False:
            return(f"Error: {test_name} failed")
        else:
            return None
