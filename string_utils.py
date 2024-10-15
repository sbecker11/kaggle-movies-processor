import json
from decimal import Decimal
import pandas as pd
import math
from enum import Enum


# use SpecialChars.ELIPSIS_CHAR.value to get the actual character
class SpecialChars(Enum):
    ALPHA_CHAR = 'α'
    BETA_CHAR = 'β'
    CHI_CHAR = 'χ'
    DEGREE_CHAR = '°'
    DELTA_CHAR = 'δ'
    ELIPSIS_CHAR = '…'
    EPSILON_CHAR = 'ε'
    ETA_CHAR = 'η'
    GAMMA_CHAR = 'γ'
    INFINITY_CHAR = '∞'
    KAPPA_CHAR = 'κ'
    LAMBDA_CHAR = 'λ'
    MICRO_CHAR = 'µ'
    MU_CHAR = 'μ'
    NU_CHAR = 'ν'
    OMEGA_CHAR = 'Ω'
    PHI_CHAR = 'φ'
    PI_CHAR = 'π'
    PLUS_MINUS_CHAR = '±'
    PSI_CHAR = 'ψ'
    RHO_CHAR = 'ρ'
    SIGMA_CHAR = 'Σ'
    SQRT_CHAR = '√'
    TAU_CHAR = 'τ'
    THETA_CHAR = 'θ'
    ZETA_CHAR = 'ζ'

# Define an enumeration for justification styles
class Justify(Enum):
    LEFT = 'left'
    CENTER = 'center'
    RIGHT = 'right'

def print_wrapped_list(title, indent=None,  wrap=5, list=[]):
    # Print a list of items in a wrapped format
    # where each row has an optional indent and a
    # maximum number of wrap items on each row.
    # prints nothing if list is None or empty
    if not list or len(list) == 0:
        return
    if title:
        print(title)
        
    if not indent:
        indent = ''
    elif isinstance(indent, int):
        indent = ' ' * indent
    elif not isinstance(indent, str):
        raise ValueError("indent must be an integer or a string")
    if len(indent) > 20:
        raise ValueError("indent must be less than 20 characters")
    ll = len(list)
    for i in range(0, ll, wrap):
        j = min(i+wrap, ll)
        print(f"{indent}{list[i:j]}")

def format_engineering_value(value):
    # Format a numeric value to a string in engineering notation
    if value is None or not isinstance(value, (int, float)):
        return ''
    if math.isnan(value):
        return 'NaN'
    # Format a numeric value in engineering notation
    decimal_value = Decimal(value)
    engineering_format = '{:e}'.format(decimal_value)
    
    # Split the engineering notation into mantissa and exponent
    mantissa, exponent = engineering_format.split('e')
    exponent = int(exponent)
    if exponent == 0:
        return mantissa
    
    # Adjust the exponent to be a multiple of 3
    exponent_adjusted = exponent - (exponent % 3)
    
    # Adjust the mantissa accordingly
    mantissa_adjusted = Decimal(mantissa) * (10 ** (exponent % 3))

    # Combine the adjusted mantissa and exponent
    engineering_notation_value = '{:.3f}e{}'.format(mantissa_adjusted, exponent_adjusted)

    # Return the string cast-ed value. use format_string to format the string
    return str(engineering_notation_value)
    
    
def format_string(value, val_size, fill_width, justify):
    # cast value to string if needed, defaulting to a single space
    # truncate to the specified length adding an ellipsis character if needed
    # and then justify to fill the specified fill_width.
    if not value or not isinstance(value, str) or len(value.strip()) == 0 :
        return ' ' * fill_width
    value = value.replace('\n', ' ').replace('\t', ' ')
    if len(value) > val_size:
        value = f"{value[:val_size-1]}{SpecialChars.ELIPSIS_CHAR.value}"
    if justify == Justify.LEFT:
        return value.ljust(fill_width)
    elif justify == Justify.RIGHT:
        return value.rjust(fill_width)
    else:
        return value.center(fill_width)
    
def format_value(value, val_size, fill_width, justify=None):
    # Truncate the value to the specified length and then
    # format it to fill or fit within the specified width.
    # for str values, truncate to max_chars and add ellipsis.
    # NaN and numeric values are right justified
    # str values are left justified.
    #
    # *Note for numeric values: the numeric value's natural 
    # string length exceeds the val_size then format it 
    # in engineering notation (hopefully it fits)
    if not isinstance(value, bool) and value is None:
        value = ' ' * fill_width
        return format_string(value, val_size, fill_width, justify=(justify or Justify.LEFT))
    elif isinstance(value, bool):
        value = str(value)
        return format_string(value, val_size, fill_width, justify=(justify or Justify.LEFT))
    elif isinstance(value, (int, float)):
        if len(str(value)) > val_size:  # see *Note above
            value = format_engineering_value(value)
        else:
            value = str(value)
        return format_string(value, val_size, fill_width, justify=(justify or Justify.RIGHT))
    elif isinstance(value, str):
        if value.isnumeric():
            value = int(value.strip()) if value.find('.') < 0 else float(value.strip())
            if len(str(value)) > val_size:  # see *Note above
                value = format_engineering_value(value)
            else:
                value = str(value)
            return format_string(value, val_size, fill_width, justify=(justify or Justify.RIGHT))
        else:
            return format_string(value, val_size, fill_width, justify=(justify or Justify.LEFT))
    elif pd.isna(value):
        return format_string(value, val_size, fill_width, justify=(justify or Justify.RIGHT))
    else:
        json_str = None
        if isinstance(value, (dict, list, tuple, object)):
            try:
                json_str = json.dumps(value)
            except json.JsonDecodeError:
                pass
        if json_str and json_str != 'null':
            value = json_str
        return format_string(value, val_size, fill_width, justify=(justify or Justify.RIGHT))

