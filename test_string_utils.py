from unittest import TestCase

from string_utils import format_value, Justify, SpecialChars, format_engineering_value, parse_engineering_value

class TestStringUtils(TestCase):
  
    def test_format_value(self):
        # None test
        value = None
        val_size = 10
        fill_width = 12
        result = format_value(value, val_size, fill_width).replace(' ', '_')
        expected = '_' * fill_width
        self.assertEqual(expected, result, "Expected: {expected}, Got: {result}")

        # Bool True test
        value = True
        val_size = 10
        fill_width = 12
        result = format_value(value, val_size, fill_width, justify=Justify.CENTER).replace(' ', '_')
        expected = '____True____'
        self.assertEqual(expected, result, "Expected: {expected}, Got: {result}")

        # Bool False test
        value = False
        val_size = 3
        fill_width = 5
        result = format_value(value, val_size, fill_width, justify=Justify.CENTER).replace(' ', '_')
        expected = f'_Fa{str(SpecialChars.ELIPSIS_CHAR.value)}_'
        self.assertEqual(expected, result, "Expected: {expected}, Got: {result}")

        # Big integer test
        value = 1234567890.1234567890
        val_size = 10
        fill_width = 12
        result = format_value(value, val_size, fill_width).replace(' ', '_')
        expected = '___1.235e+09'
        self.assertEqual(expected, result, "Expected: {expected}, Got: {result}")
        
        # Negative Big integer test
        value = -1234567890.1234567890
        val_size = 10
        fill_width = 12
        result = format_value(value, val_size, fill_width).replace(' ', '_')
        expected = '__-1.235e+09'
        self.assertEqual(expected, result, "Expected: {expected}, Got: {result}")
        
        # Negative Big integer test, center justified
        value = -1234567890.1234567890
        val_size = 10
        fill_width = 12
        result = format_value(value, val_size, fill_width, justify=Justify.CENTER).replace(' ', '_')
        expected = '_-1.235e+09_'
        self.assertEqual(expected, result, "Expected: {expected}, Got: {result}")

        # Big engineering notation test
        value = 1.234e-99
        val_size = 10
        fill_width = 12
        result = format_value(value, val_size, fill_width).replace(' ', '_')
        expected = '___1.234e-99'
        self.assertEqual(expected, result, "Expected: {expected}, Got: {result}")
  
        # Negative Big engineering notation test
        value = -1.23466789e-99
        val_size = 10
        fill_width = 12
        result = format_value(value, val_size, fill_width, justify=Justify.CENTER).replace(' ', '_')
        expected = '_-1.235e-99_'
        self.assertEqual(expected, result, "Expected: {expected}, Got: {result}")

        # Negative Big engineering notation center justified test
        value = -1.23466789e-99
        val_size = 10
        fill_width = 12
        result = format_value(value, val_size, fill_width, justify=Justify.CENTER).replace(' ', '_')
        expected = '_-1.235e-99_'
        self.assertEqual(expected, result, "Expected: {expected}, Got: {result}")

        # long string test
        value = 'abcdefghijklmnopqrstuvwxyz'
        val_size = 5
        fill_width = 7
        result = format_value(value, val_size, fill_width, justify=Justify.CENTER).replace(' ', '_')
        expected = f'_abcd{SpecialChars.ELIPSIS_CHAR.value}_'
        self.assertEqual(expected, result, "Expected: {expected}, Got: {result}")
        
        # object empty dict test
        value = {}
        val_size = 5
        fill_width = 7
        result = format_value(value, val_size, fill_width, justify=Justify.CENTER).replace(' ', '_')
        expected = '___{}__'
        self.assertEqual(expected, result, "Expected: {expected}, Got: {result}")

        # object long dict test
        value = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
        val_size = 5
        fill_width = 7
        result = format_value(value, val_size, fill_width, justify=Justify.CENTER).replace(' ', '_')
        expected = '_{"a"' + SpecialChars.ELIPSIS_CHAR.value + '_'
        self.assertEqual(expected, result, "Expected: {expected}, Got: {result}")

    def test_engineering_format(self):
        test_strings = ['1.230e+03', '1.230e-03', '-1.230e+03', '0.000e+00', 'NaN', 'invalid']
        test_values =    [1230.0, 0.00123, -1230.0, 0.0, None, None]
        if len(test_strings) != len(test_values):
            raise ValueError("test_strings and test_values must have the same length")
        
        for i in range(len(test_strings)):
            formatted_result = format_engineering_value(test_values[i])
            expected_result = '' if test_values[i] is None else test_strings[i] 
            if formatted_result != expected_result:
                self.fail(f"format_engineering_value('{test_values[i]}') -> {formatted_result} != {expected_result}")
            else:
                self.assertEqual(formatted_result, expected_result, f"format_engineering_value('{test_values[i]}') -> {expected_result}")

    def test_engineering_parse(self):
        test_strings = ['1.230e+03', '1.230e-03', '-1.230e+03', '0.000e+00', 'NaN', 'invalid']
        test_values =    [1230.0, 0.00123, -1230.0, 0.0, None, None]
        if len(test_strings) != len(test_values):
            raise ValueError("test_strings and test_values must have the same length")
        
        for i in range(len(test_strings)):
            parsed_result = parse_engineering_value(test_strings[i])
            if parsed_result != test_values[i]:
                self.fail(f"parse_engineering_value('{test_strings[i]}') -> {parsed_result} != {test_values[i]}")
            else:
                self.assertEqual(parsed_result, test_values[i], f"parse_engineering_value('{test_strings[i]}') -> {parsed_result}")

    def test_engineering_format_jnversion(self):
        # test f'(f(x)) = x  for several test_values of x
        test_values = [1.23e+03, 123.4, 0.00123, -1230.0, 0.0, None]    
        for test_value in test_values:
            formatted_result = format_engineering_value(test_value)
            parsed_result = parse_engineering_value(formatted_result)
            self.assertEqual(test_value, parsed_result, f"format_engineering_value('{test_value}') -> '{formatted_result}' -> {parsed_result}")