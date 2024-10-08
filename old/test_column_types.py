from column_types import extract_dict_string, extract_list_of_dict_string, get_json_parseable_string, extract_integer, extract_float, extract_boolean, extract_ymd_datetime
from unittest import TestCase
import pandas as pd

class TestMoviewColumnTypes(TestCase):
    
    def test_dtype_text_to_date(self):

        data = {'date_column': ['2023-01-01', '2023-02-01', '2023-03-01']}
        df = pd.DataFrame(data)

        # Convert the column to datetime
        df['date_column'] = pd.to_datetime(df['date_column'])
        v = df['date_column'].iloc[0]
        print(f"v:{v} type:{type(v)}")
        self.assertIsInstance(v, pd.Timestamp, "Error should have returned a pandas Timestamp")
        print(df)
        print(df.dtypes)
        print('done')
            
        # to run this test function in isolation use the following command
        # python -m unittest -k test_dtype_text_to_date test_column_types.py

    
    def test_get_json_parseable_string(self):
        case_a =     '[{"id": 16, "name": "le\'Animation1"}, {"id": 17, "name": null}]'
        result_a = get_json_parseable_string(case_a)
        self.assertEqual(case_a, result_a, "already parseable so should have returned the same value")

        case_b =     "[{'id': 16, 'name': 'O'Connor'}, {'id': 17, 'name': 'Action'}]"
        expected_b = '[{"id": 16, "name": "O\'Connor"}, {"id": 17, "name": "Action"}]'
        result_b = get_json_parseable_string(case_b)
        self.assertEqual(result_b, expected_b, f"should have returned expected value: {expected_b}") 

        case_c =     "[{'id': 16, 'name': 'O'Connor'}, {'id': 17, 'name': None}]"
        expected_c = '[{"id": 16, "name": "O\'Connor"}, {"id": 17, "name": null}]'
        result_c = get_json_parseable_string(case_c)
        self.assertEqual(result_c, expected_c, f"should have returned expected value: {expected_c}") 

    def test_extract_integer(self):
        s = "123"
        y = extract_integer(s)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, int, "Error should have returned an integer")
        self.assertEqual(y, 123, "Error should have returned 123")
        
        s = "123.14"
        y = extract_integer(s)
        self.assertIsNone(y, "Error should have returned None")
        
        s = "123E-10"
        y = extract_integer(s)
        self.assertIsNone(y, "Error should have returned None")
        
        s = "  "
        y = extract_integer(s)
        self.assertIsNone(y, "Error should have returned None")
        
        s = "123.00000"
        y = extract_integer(s)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, int, "Error should have returned an integer")
        self.assertEqual(y, 123, "Error should have returned 123")

    def test_extract_float(self):
        s = "3.14"
        y = extract_float(s)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, float, "Error should have returned a float")
        self.assertEqual(y, 3.14, "Error should have returned 3.14")

        s = "3.14.14"
        y = extract_float(s)
        self.assertIsNone(y, "Error should have returned None")

        s = "3.14E-10"
        y = extract_float(s)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, float, "Error should have returned a float")
        
        x = 8.387519
        y = extract_float(x)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, float, "Error should have returned a float")
        self.assertEqual(y, x, f"Error should have returned {x}")


    def test_extract_boolean(self):
        s = "True"
        y = extract_boolean(s)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, bool, "Error should have returned a boolean")
        self.assertEqual(y, True, "Error should have returned True") 

        s = "False"
        y = extract_boolean(s)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, bool, "Error should have returned a boolean")
        self.assertEqual(y, False, "Error should have returned False") 

        s = "Falsee"
        y = extract_boolean(s)
        self.assertIsNone(y, "Error should have returned None")

        s = None
        y = extract_boolean(s)
        self.assertIsNone(y, "Error should have returned None")

        s = "  "
        y = extract_boolean(s)
        self.assertIsNone(y, "Error should have returned None")
        
    def test_extract_dict_string(self):
        s = "{'id': 16, 'name': 'Animation7'}"
        y = extract_dict_string(s)
        self.assertIsNone(y, "Error should have returned None")

        s = "{'id': 16, 'name': 'le\'Animation8'}"
        y = extract_dict_string(s)
        self.assertIsNone(y, "Error should have returned None")
        
        s = '{"id": 9068, "name": "The Prophecy Collection", "poster_path": "/pU4wvBeirFDNk8rs9tsGZLa7Kyb.jpg", "backdrop_path": None}'
        y = extract_dict_string(s)
        self.assertEquals(y, "Input is already json parseable and can be parsed by json.loads to return a dict")  

    def test_extract_list_of_dict_string(self):
        s = '[{"id": 16, "name": "AnimationA"}, {"id": 35, "name": "Comedy"}, {"id": 10751, "name": None}]'
        y = extract_list_of_dict_string(s)
        self.assertIsEqual(y, s, f"Error should  have returned {s}")

        s = "[{'id': 16, 'name': 'AnimationA'}, {'id': 35, 'name': 'Comedy'}, {'id': 10751, 'name': 'Family'}]"
        y = extract_list_of_dict_string(s)
        self.assertIsNone(y, "Error should  have returned None")
                
        s = "[{'id': 16, 'name': 'AnimationB'}, [1,2], 3]"
        y = extract_list_of_dict_string(s)
        self.assertIsNone(y, "Error should have returned None")
        
        s = "[]"
        y = extract_list_of_dict_string(s)
        self.assertIsNone(y, "Error should have returned None")
                
        s = '[{"name": "Yermoliev", "id": 88753}]'
        y = extract_list_of_dict_string(s)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, list, "Error should have returned a list")
        self.assertEqual(y, s, f"Error should have returned {s}")

        s = '[{}]'
        y = extract_list_of_dict_string(s)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, list, "Error should have returned a list")
        self.assertTrue(len(y) == 1, "Error should have returned a list of length 1")
        
        s = "[{}]"
        y = extract_list_of_dict_string(s)
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertIsInstance(y, list, "Error should have returned a list")
        self.assertTrue(len(y) == 1, "Error should have returned a list of length 1")

    def test_extract_ymd_datetime(self):
        s = "2022-10-11"
        y = extract_ymd_datetime(s)
        expected = pd.to_datetime("2022-10-11", format="%Y-%m-%d")
        self.assertIsNotNone(y, "Error should not have returned None")
        self.assertEqual(y, expected, f"Error should have returned {expected}")
        
        s = "2022-10-1"
        y = extract_ymd_datetime(s)
        self.assertIsNone(y, "Error should have returned None")
        
        s = "2022-10-11T14:14:14.123=06:00"
        y = extract_ymd_datetime(s)
        self.assertIsNone(y, "Error should have returned None")


