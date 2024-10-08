from unittest import TestCase

from string_utils import format_value, Justify, SpecialChars

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
        expected = '_____1.235e9'
        self.assertEqual(expected, result, "Expected: {expected}, Got: {result}")
        
        # Negative Big integer test
        value = -1234567890.1234567890
        val_size = 10
        fill_width = 12
        result = format_value(value, val_size, fill_width).replace(' ', '_')
        expected = '____-1.235e9'
        self.assertEqual(expected, result, "Expected: {expected}, Got: {result}")
        
        # Negative Big integer test, center justified
        value = -1234567890.1234567890
        val_size = 10
        fill_width = 12
        result = format_value(value, val_size, fill_width, justify=Justify.CENTER).replace(' ', '_')
        expected = '__-1.235e9__'
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

