from movie_column_types import extract_dict, fix_quotes_for_json, json_load_string, json_load_dict_string, extract_integer, extract_float, extract_boolean, extract_list_of_dicts, extract_ymd_datetime
from unittest import TestCase
import pandas as pd

class TestMoviewColumnTypes(TestCase):
    
    def test_fix_quotes_for_json(self):
        case_a =     "[{'id': 16, 'name': 'le'Animation1'}, {'id': 17, 'name': 'Action'}]"
        expected_a = '[{"id": 16, "name": "le\\u0027Animation1"}, {"id": 17, "name": "Action"}]'
        result_a = fix_quotes_for_json(case_a)
        self.assertEqual(expected_a, result_a, f"expected {expected_a} but got {result_a}")

        case_b =     "[{'id': 16, 'name': 'O'Connor'}, {'id': 17, 'name': 'Action'}]"
        expected_b = '[{"id": 16, "name": "O\\u0027Connor"}, {"id": 17, "name": "Action"}]'
        result_b = fix_quotes_for_json(case_b)
        self.assertEqual(expected_b, result_b, f"expected {expected_b} but got {result_b}")

    def test_json_load_string(self):
        s = "[{'id': 16, 'name': 'Animation2'}]"
        x = json_load_string(s)
        if x is None:
            print("Error should have returned a list")
            return False
        
        s = "[{'id': 16, 'name': 'le'Animation3'}]"
        x = json_load_string(s)
        if x is None:
            print("Error should have returned a list")
            return False
        
        s = "{'id': 16, 'name': 'Animation4'}"
        x = json_load_string(s)
        if x is None or not isinstance(x, dict):
            print("Error should have returned a dict")
            return False

    def test_json_load_dict_string(self):
        s = "{'id': 16, 'name': 'Animation5'}"
        x = json_load_dict_string(s)
        self.assertIsNotNone(x, "Error should not have returned None")
        self.assertIsInstance(x, dict, "Error should have returned a dict")

        s = "{'id': 16, 'name': 'le\\'Animation6'}"
        x = json_load_dict_string(s)
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
        
    def test_extract_dict(self):
        x = "{'id': 16, 'name': 'Animation7'}"
        y = extract_dict(x)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, dict, "Error should have returned a dict") 
        self.assertEqual(y, {"id": 16, "name": "Animation7"}, "Error should have returned {'id': 16, 'name': 'Animation7'}")

        x = "{'id': 16, 'name': 'le\'Animation8'}"
        y = extract_dict(x)
        expected = {"id": 16, "name": "le'Animation8"}
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, dict, "Error should have returned a dict") 
        self.assertEqual(y, expected, f"Error should have returned {expected}")
        
        x = "{'id': 9068, 'name': 'The Prophecy Collection', 'poster_path': '/pU4wvBeirFDNk8rs9tsGZLa7Kyb.jpg', 'backdrop_path': None}"
        y = extract_dict(x)
        expected = {"id": 9068, "name": "The Prophecy Collection", "poster_path": "/pU4wvBeirFDNk8rs9tsGZLa7Kyb.jpg", "backdrop_path": None}
        self.assertIsNotNone(y, "Error should not have returned None")  
        self.assertIsInstance(y, dict, "Error should have returned a dict") 
        self.assertEqual(y, expected, f"Error should have returned {expected}")  

    def test_extract_list_of_dicts(self):
        x = "[{'id': 16, 'name': 'AnimationA'}, {'id': 35, 'name': 'Comedy'}, {'id': 10751, 'name': 'Family'}]"
        expected = [{"id": 16, "name": "AnimationA"}, {"id": 35, "name": "Comedy"}, {"id": 10751, "name": "Family"}]
        y = extract_list_of_dicts(x)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, list, "Error should have returned a list")
        self.assertEqual(y, expected, f"Error should have returned {expected}")
                
        x = "[{'id': 16, 'name': 'AnimationB'}, [1,2], 3]"
        y = extract_list_of_dicts(x)
        self.assertIsNone(y, "Error should have returned None")
        
        x = "[]"
        y = extract_list_of_dicts(x)
        self.assertIsNone(y, "Error should have returned None")
                
        x = [{"name": "Yermoliev", "id": 88753}]
        y = extract_list_of_dicts(x)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, list, "Error should have returned a list")
        self.assertEqual(y, x, f"Error should have returned {x}")

        x = '[{}]'
        y = extract_list_of_dicts(x)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, list, "Error should have returned a list")
        self.assertTrue(len(y) == 1, "Error should have returned a list of length 1")
        
        x = "[{}]"
        y = extract_list_of_dicts(x)
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
        self.assertIsNone(y, "Error should have returned None")
        
        x = "2022-10-11T14:14:14.123=06:00"
        y = extract_ymd_datetime(x)
        self.assertIsNone(y, "Error should have returned None")


