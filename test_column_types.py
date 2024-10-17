from column_types import extract_dict, extract_object, extract_string, extract_integer, extract_float, extract_boolean, extract_list_of_dict, extract_ymd_datetime, p_typed_value, fNaN, fInf
from unittest import TestCase
import pandas as pd

class TestColumnTypes(TestCase):

    def test_extract_string(self):
        s = "[{'id': 16, 'name': 'Animation2'}]"
        x = extract_string(s)
        self.assertEqual(x, s, "Error should be equal")
        
        s =        "  [{'id': 16, 'name': 'le\\'Animation3'}]  "
        expected = "[{'id': 16, 'name': 'le\\'Animation3'}]"
        x = extract_string(s)
        self.assertEqual(x, expected, f"Error should match expected stripped version of s {expected}")

    def test_extract_dict(self):
        s = "{'id': 16, 'name': 'Animation5'}"
        x = extract_dict(s)
        self.assertIsNotNone(x, "Error should not have returned None")
        self.assertIsInstance(x, dict, "Error should have returned a dict")

        s = "{'id': 16, 'name': 'le\\\'Animation6'}"
        x = extract_dict(s)
        self.assertIsNotNone(x, "Error should not have returned None")
        self.assertIsInstance(x, dict, "Error should have returned a dict")

    def test_extract_integer(self):
        x = "123"
        y = extract_integer(x)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, int, "Error should have returned an integer")
        self.assertEqual(123, y, "Error should have returned 123")
        
        x = "123.14"
        y = extract_integer(x)
        self.assertEqual(123,y, "Error should have returned 123")
        
        x = "123E-10"
        y = extract_integer(x)
        self.assertEqual(0, y, "Error should have returned 0")
        
        x = "  "
        y = extract_integer(x)
        self.assertIsNone(y, "Error should have returned None")
        
        x = "123.00000"
        y = extract_integer(x)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, int, "Error should have returned an integer")
        self.assertEqual(123, y, "Error should have returned 123")

    def test_extract_float(self):
        x = "3.14"
        y = extract_float(x)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, float, "Error should have returned a float")
        self.assertEqual(3.14, y, "Error should have returned 3.14")

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
        self.assertEqual(x, y, f"Error should have returned {x}")

    def test_extract_boolean(self):
        x = "True"
        y = extract_boolean(x)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, bool, "Error should have returned a boolean")
        self.assertEqual(True, y, "Error should have returned True") 

        x = "False"
        y = extract_boolean(x)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, bool, "Error should have returned a boolean")
        self.assertEqual(False, y, "Error should have returned False") 

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
        case_a = "[{'id': 16, 'name': 'le\\'Animation1'}, {'id': 17, 'name': 'Action'}]"
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
        error_message = self.print_and_compare("cast all values to float", input_data, expected_data, extract_float)
        if error_message:
            self.fail(error_message)
    
    def test_extract_boolean_from_all_values(self):
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
        error_message = self.print_and_compare("test_extract_boolean_from_all_valuess", input_data, expected_data, extract_boolean)
        if error_message:
            self.fail(error_message)

    def test_extract_integer_from_all_values(self):
        # if integer columns dtypes are not specified, then 
        # because any column with both None (or Nan) and 
        # numeric values is considered mixed. and mixed 
        # columns are cast to float because NaN is a 
        # floating-point representation
        # of missing data
        input_data = {
            'A': [1, 2, 'a'],
            'B': [5.5, False, None],
            'C': [7, -8.5, 'B']
        }
        
        expected_data = {
            'A': [1, 2, None],
            'B': [6, None, None],
            'C': [7, -9, None]
        }
        error_message = self.print_and_compare("test_extract_integer_from_all_values", input_data, expected_data, extract_integer)
        if error_message:
            self.fail(error_message)
            
    def test_extract_string_from_all_values(self):
        input_data = {
            'A': [1, '2', '{"a": 7}' ],
            'B': ['happy', 'day\\\'s', '[{"b": 8},{"c": 9}]' ],
            'C': [7, True, '(1,2,3)']
        }
        expected_data = {
            'A': ['1', '2', '{"a": 7}' ],
            'B': ['happy', 'day\\\'s', '[{"b": 8},{"c": 9}]' ],
            'C': ['7', 'True', '(1,2,3)']
        }
        error_message = self.print_and_compare("test_extract_string_from_all_valuess", input_data, expected_data, extract_string)
        if error_message:
            self.fail(error_message)
        print()

    # return an error_message if any of the result values
    # don't match the expected values.
    # otherwise, return None if there are no errors
    def print_and_compare(self, test_name, data_input, data_expected, column_type_extractor):
        print('=' * 80)
        print(test_name)
        
        print("df_input:------------------------------------")
        df_input = pd.DataFrame(data_input)
        print(df_input)
        
        print("df_expected:---------------------------------")
        df_expected = pd.DataFrame(data_expected)
        print(df_expected)
        
        print("df_result:-----------------------------------")
        df_result = self.map_all_columns(df_input, column_type_extractor)
        print(df_result)
        
        print(f"{extract_integer(6.0)}")
        
        error_message = self.df_compare(test_name, df_expected, df_result)
        if error_message:
            self.fail(error_message)

    def map_all_columns(self, df, column_type_extractor):
       return df.apply(lambda col: col.map(column_type_extractor))
   
    def df_compare(self, test_name, df_exp, df_rst):
        str_exp = df_exp.to_string().replace('\n', '')
        str_rst = df_rst.to_string().replace('\n', '')
        mismatch_index = self.first_mismatch_index(str_exp, str_rst)
        if mismatch_index != -1:
            error_lines = []
            error_lines.append(f"df_exp: {str_exp}")
            error_lines.append(f"df_rst: {str_rst}")
            line1 = " " * 8
            line2 = " " * 8
            for i in range(len(df_exp.to_string().replace('\n',''))):
                line1 += str(i % 10)
                line2 += str((i // 10) % 10)
            error_lines.append(line1)
            error_lines.append(line2)
            error_lines.append("       |"+('-' * mismatch_index) + '^')
            return f"{test_name} Failed at mismatch index: {mismatch_index}\n"  + '\n'.join(error_lines)
        else:
            return None
        

    def first_mismatch_index(self, str1, str2):
        min_length = min(len(str1), len(str2))
        for i in range(min_length):
            if str1[i] != str2[i]:
                return i
        if len(str1) != len(str2):
            return min_length
        return -1  # Return -1 if the strings are identical
    
    def test_column_type_extractors(self):
        self.assertTrue(extract_integer(fNaN) is None, "Error should have returned None")
        self.assertTrue(extract_integer(fInf) is None, "Error should have returned None")
        self.assertTrue(extract_integer(-fInf) is None, "Error should have returned None")
        self.assertTrue(extract_integer(None) is None, "Error should have returned None")
        self.assertTrue(extract_integer(True) is None, "Error should have returned None")
        self.assertTrue(extract_integer(False) is None, "Error should have returned None")
        self.assertTrue(extract_integer("hot's") is None, "Error should have returned None")
        self.assertTrue(extract_integer("") is None, "Error should have returned None")
        
        self.assertTrue(extract_float(fNaN) is None, "Error should have returned None")
        self.assertTrue(extract_float(fInf) is None, "Error should have returned None")
        self.assertTrue(extract_float(-fInf) is None, "Error should have returned None")
        self.assertTrue(extract_float(None) is None, "Error should have returned None")
        self.assertTrue(extract_float(True) is None, "Error should have returned None")
        self.assertTrue(extract_float(False) is None, "Error should have returned None")
        self.assertTrue(extract_float(False) is None, "Error should have returned None")
        self.assertTrue(extract_float("hot's") is None, "Error should have returned None")
        self.assertTrue(extract_float("") is None, "Error should have returned None")

        self.assertTrue(extract_boolean(fNaN) is None, "Error should have returned None")
        self.assertTrue(extract_boolean(fInf) is None, "Error should have returned None")
        self.assertTrue(extract_boolean(-fInf) is None, "Error should have returned None")
        self.assertTrue(extract_boolean(None) is None, "Error should have returned None")
        self.assertTrue(extract_boolean(True) is True, "Error should have returned True")
        self.assertTrue(extract_boolean(False) is False, "Error should have returned False")
        self.assertTrue(extract_boolean("hot's") is None, "Error should have returned None")
        self.assertTrue(extract_boolean("") is None, "Error should have returned None")

        self.assertTrue(extract_string(fNaN) == 'NaN', "Error should have returned 'nan'")
        self.assertTrue(extract_string(fInf) == 'Inf', "Error should have returned 'finf'")
        self.assertTrue(extract_string(-fInf) == '-Inf', "Error should have returned '-finf'")
        self.assertTrue(extract_string(None) == 'None', "Error should have returned 'None'")
        self.assertTrue(extract_string(True) == 'True', "Error should have returned 'True'")
        self.assertTrue(extract_string(False) == 'False', "Error should have returned 'False'")
        self.assertTrue(extract_string("hot's") == "hot's", "Error should have returned hot's")
        self.assertTrue(extract_string("") == "", "Error should have returned ''")

        values = [fNaN, True, False, 'True', 'False', 'true', 'false', 1, '1', 1.0, '1.0', None, 'None', "hot's", 'hot\\\'s']
        column_type_extractors  = [extract_boolean, extract_integer, extract_float, extract_string]
        for value in values:
            for extractor in column_type_extractors:
                result = extractor(value)
                print(f"{extractor.__name__}({p_typed_value(value)}) -> {p_typed_value(result)}")
  
        
        
        