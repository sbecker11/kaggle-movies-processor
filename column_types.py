import ast
import json
import math
import re

import numpy as np
import pandas as pd

from thread_utils import run_with_message

from column_errors_logger import logger as process_columns_logger
import textwrap

fnan = fNaN = np.nan
finf = fInf = np.inf

# return a string representation of the 
# type of the given value
def p_typed_value(x):
    if np.isna(x):
        return 'f:NaN'          # NaN is a float
    if np.isinf(x):
        return 'f:Inf'          # NaN is a float
    if np.isneginf(x):
        return '-f:Inf'          # NaN is a float
    type_str = type(x).__name__
    if type_str == 'NoneType':
        return 'f:None'        # none is a float
    if type_str == 'bool':
        return f'b:{x}'
    if type_str == 'int':
        return f'd:{x}'
    if type_str == 'float':
        return f'f:{x}'
    if type_str == 'str':
        return f's:{x}'
    raise ValueError(f"Unknown type {type_str}")

###### ---- string functions ---- ######

def cast_to_string(x):
    if x is None:
        return 'None'
    if isinstance(x, float):
        if np.isnan(x):
            return 'NaN'
        if np.isinf(x):
            return 'Inf' if x > 0 else '-Inf'
    try:
        return str(x)
    except ValueError:
        return None

# process a string, returning None if the string is empty or Nan, Inf or negInf
def extract_string(x):
    if x is None:
        return None
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return None
    if isinstance(x, str):
        x = x.strip()
        if len(x) == 0:
            return None
        return x
    return None

def is_string(s):
    return extract_string(s) is not None

###### ---- boolean functions ---- ######

def cast_to_boolean(x):
    try:
        if x is None or (isinstance(x, (int, float)) and (np.isnan(x) or np.isinf(x) or np.isneginf(x))):
            return None
        return bool(x)
    except (ValueError, TypeError):
        return None

# extract a boolean from a boolean or a string
# return None if the string is empty or does not have a boolean pattern
def extract_boolean(x):
    # Check if x is None and return None if it is
    if x is None:
        return None
    
    # Check if x is NaN or infinity and return None if it is
    try:
        if np.isnan(x) or np.isinf(x):
            return None
    except TypeError:
        pass
    
    # Check if x is already a boolean and return it if it is
    if isinstance(x, bool):
        return x
    
    # Attempt to extract a string from x
    s = extract_string(x)
    
    # If a non-empty string was extracted
    if s is not None:
        # Convert to lowercase for comparison
        s = s.lower()
        
        # Check if the string represents a boolean value and return the corresponding boolean
        if s == "true":
            return True
        if s == "false":
            return False
    
    # If none of the above conditions were met, return None
    return None

###### ---- integer functions ---- ######

def cast_to_integer(x):
    if (x is None) or isinstance(x, bool):
        return None
    if isinstance(x, int):
        return x
    if isinstance(x, float):
        if np.isnan(x) or np.isinf(x) or np.isneginf(x):
            return None
        return round_float_to_integer(x)
    if isinstance(x, str):
        s = x.strip()
        if s.isdigit():
            return int(s)
        v = float_from_string(s)
        if v is not None:
            return round_float_to_integer(v)
    try:
        return int(x)
    except ValueError:
        return None

# attempt to extract an integer from a an integer, float or string
# return None if the string is empty or cannot be converted to an integer
def extract_integer(x):
    if (x is None) or isinstance(x, bool):
        return None
    if np.isnan(x) or np.isinf(x) or np.isneginf(x):
        return None
    if isinstance(x, int):
        return x
    if isinstance(x, float):
        return round_float_to_integer(x)
    if isinstance(x, str):
        s = x.strip()
        if s.isdigit():
            return int(s)
        v = float_from_string(s)
        if v is not None:
            return round_float_to_integer(v)
    return None

def is_integer(s):
    return extract_integer(s) is not None

def round_float_to_integer(x):
    if type(x) is not float:
        raise ValueError(f"input must be a float, not ${x.__class__.__name__}")
    if x is None or np.isnan(x) or np.isinf(x) or np.isneginf(x):
        return None
    if x < 0.0:
        v = -math.floor(0.5-x)
    elif x > 0.0:
        v = math.floor(x+0.5)
    else:
        return 0
    try:
        s = str(v)
        if s.endswith('.0'):
            v = int(s[:-2])
        return v
    except ValueError:
        return 0

###### ---- float functions ---- ######
# cast a value to a float or return None if the value is None or a boolean
def cast_to_float(x):
    if (x is None) or isinstance(x, bool):
        return None
    if isinstance(x, float):
        if np.isnan(x) or np.isinf(x) or np.isneginf(x):
            return None
        return x
    if isinstance(x, str):
        s = x.strip()
        if s.isdigit():
            return float(int(s))
        v = float_from_string(x)
        if v is not None:
            return v
    try:
        return float(x)
    except ValueError:
        return None

    return None

# return a float from a string or None if the string 
# is empty or does not have a float pattern
def float_from_string(s):
    if not isinstance(s, str):
        raise ValueError("input must be a string")
    try:
        if s.isdigit():
            return float(int(s))
        if has_float_pattern(s):
            return float(s) 
    except ValueError:
        return None
    
def has_float_pattern(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# extract a float from a float, int or string
def extract_float(x):
    # Check if x is None or a boolean and return None if it is
    if x is None or isinstance(x, bool):
        return None
    
    # Check if x is NaN or infinity and return None if it is
    try:
        if np.isnan(x) or np.isinf(x):
            return None
    except TypeError:
        pass
    
    # Check if x is already a float and return it if it is
    if isinstance(x, float):
        return x
    
    # Check if x is an integer and convert it to float
    if isinstance(x, int):
        return float(x)
    
    # Attempt to extract a string from x
    s = extract_string(x)
    
    # If a non-empty string was extracted
    if s is not None:
        try:
            return float(s)
        except ValueError:
            return None
    
    # If none of the above conditions were met, return None
    return None

def is_float(s):
    return extract_float(s) is not None

def is_numeric(s):
    return is_integer(s) or is_float(s)

###### ---- object functions ---- ######

# extract a list or a dict from the given string
# or return None if the string has the wrong format
# or cannot be json-parsed
def extract_object(input_str):
    if input_str is None or not isinstance(input_str, str) or len(input_str.strip()) == 0:
        return None
    if np.isnan(input_str) or np.isinf(input_str) or np.isneginf():
        return None
   
    input_str = input_str.strip()
    
    # check if unwrapped has list, dict or tuple syntax
    if input_str[0] in ['"', "'"] and input_str[-1] == input_str[0]:
        unwrapped = input_str[1:-1].strip()
        if unwrapped[0] not in '[{(':
            return None
    
    try:
        y = json.loads(input_str)
        if isinstance(y, (list, dict)):
            return y
    except (json.JSONDecodeError, ValueError, TypeError):
        # print(f"Debug Error 1: {e}")
        # print(f"on json.loads on input_str: {input_str}")

        # try a literal evaluation
        # e.g. input_str: '[{\'name\': \'The Booking\'s Office\'}]'
        try:
            y = ast.literal_eval(input_str)
            if y is not None and isinstance(y, (list, dict)):
                return y
        except (ValueError, SyntaxError) as e:
            print(f"Debug Error 2: {e}")
            print(f"on literal eval on input_str: {input_str}")

            # replace internal single quotes with encoded form
            fixed_str = re.sub(r"(?<=\w)'(?=\w)", r'\\u0027', input_str)
            # replace all remaining single quotes with double quotes
            fixed_str = fixed_str.replace("'", '"')
            # decode the encoded single quotes
            fixed_str = fixed_str.replace('\\u0027', "'")
            # replace python None with Json null
            fixed_str = fixed_str.replace("None", "null")
            
            try:
                y = json.loads(fixed_str)
                if isinstance(y, (list, dict)):
                    return y
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                print(f"Debug Error 3: {e}")
                print(f"on json.loads on fixed_str: {fixed_str}")
                
                # If the JSON decoder fails, try to fix the quotes in the JSON string
                # This regular expression targets single quotes that are likely part of the content
                final_str = re.sub(r"(?<=\w)'(?=\w)", r'\\u0027', fixed_str)
                try:
                    y = json.loads(final_str)
                    if isinstance(y, (list, dict)):
                        return y
                except (json.JSONDecodeError, ValueError, TypeError) as e:
                    print(f"Debug Error 4: {e}")
                    print(f"json.loads on final_str: {final_str}")
                    
                    # If the JSON decoder fails again, return None
                    return None

# attempt to extract a dict object from the given string
# or return None if the string cannot be json-parsed
def extract_dict(s):
    v = extract_object(s)
    if isinstance(v, dict):
        return v
    return None

# return true if the given string 
# can be json-parsed into a possibly empty 
# dict otherwise return false
def is_dict(x):
    return extract_dict(x) is not None

# attempt to extract a list of at least one dict from 
# the given string or return None if the string 
# cannot be json-parsed
def extract_list_of_dict(s):
    v = extract_object(s)
    if v is not None and isinstance(v, list):
        if len(v) > 0:
            if all(isinstance(x, dict) for x in v):
                return v
            return None
        return None
    return None

def is_list_of_dict(x):
    return extract_list_of_dict(x) is not None

def extract_status_category(x):
    if extract_string(x) is not None:
        x = x.strip()
        if x in ["Rumored", "Planned", "In Production", "Post Production", "Released", "Canceled"]:
            return x
    return None

def is_status_category(s):
    return extract_status_category(s) is not None


###### ---- datetime functions ---- ######

# try to extract a pandas.datetime from a 
# 10-character string or return Non
def extract_ymd_datetime(s):
    t = extract_string(s)
    if t is not None and isinstance(t, str):
        # yyyy-mm-dd is strictly 10 chars in length
        if len(t) != 10:
            return None
        try:
            return pd.to_datetime(t, format="%Y-%m-%d")
        except ValueError:
            return None
    return None

def is_ymd_datetime(s):
    return extract_ymd_datetime(s) is not None

###### ---- extractpr and column_type functions ---- ######

column_type_extractors = {
    "boolean": extract_boolean,
    "dict": extract_dict,
    "integer": extract_integer,
    "list_of_dict": extract_list_of_dict,
    "string": extract_string,
    "float":  extract_float,
    "ymd_datetime": extract_ymd_datetime,
    "status_category": extract_status_category
}
column_type_casters = {
    "boolean": cast_to_boolean,
    "integer": cast_to_integer,
    "string": cast_to_string,
    "float":  cast_to_float
}
column_type_dtypes = {
    "boolean": "bool",
    "dict": "object",
    "integer": "int64",
    "list_of_dict": "object",
    "string": "string",
    "float": "float64",
    "ymd_datetime": "datetime64",
    "status_category": "string"
}
column_types = {
    "adult": "boolean",
    "belongs_to_collection": "dict",
    "budget": "integer",
    "genres": "list_of_dict",
    "homepage": "string",
    "id": "integer",
    "imdb_id": "string",
    "original_language": "string",
    "original_title": "string",
    "overview": "string",
    "popularity": "float",
    "poster_path": "string",
    "production_companies": "list_of_dict",
    "production_countries": "list_of_dict",
    "release_date": "ymd_datetime",
    "revenue": "integer",
    "runtime": "float",
    "spoken_languages": "list_of_dict",
    "status": "status_category",
    "tagline": "string",
    "title": "string",
    "video": "boolean",
    "vote_average": "float",
    "vote_count": "integer"
}

numeric_column_types = {
    "integer",
    "float"
}

def is_float_column_type(col):
    if get_column_type(col) == "float":
        return True
    return False

def is_numeric_column_type(col):
    if get_column_type(col) in numeric_column_types:
        return True
    return False

def get_numeric_columns(df):
    return [col for col in df.columns if is_numeric_column_type(col)]
    
def get_column_type(col):
    column_type = column_types.get(col)
    if column_type is not None:
        return column_type
    else:
        raise ValueError(f"Error: no column type found for column: '{col}'")
    
def get_column_dtype(col):
    column_type = get_column_type(col)
    column_dtype = column_type_dtypes.get(column_type)
    if column_dtype is not None:
        return column_dtype
    else:
        raise ValueError(f"no column dtype found for column_type:{column_type}")

def get_column_type_extractor(column_type):
    extractor = column_type_extractors.get(column_type)
    if extractor is not None:
        return extractor
    else:
        raise ValueError(f"no extractor found for column_type: {column_type}")

def get_column_extractor(col):
    return get_column_type_extractor(get_column_type(col))

def get_column_names_from_csv_file(csv_path):
    with open(csv_path, "r") as f:
        first_row = f.readline().split(',')
    column_names = [first_row[i].strip() for i in range(len(first_row))]
    if column_names is None or len(column_names) != len(first_row):
        raise ValueError("item count failure")     
    return column_names

def get_column_names_from_df(df):
    return df.columns

def verify_all_columns_have_extractors(df):
    # a ValueError will be raised on the
    # first column that has no extractor
    for col in df.columns:
        get_column_extractor(col)

def verify_column_names(csv_path, df):
    # raise ValueError if column names don't match
    csv_columns = get_column_names_from_csv_file(csv_path)
    df_columns = get_column_names_from_df(df)
    if len(csv_columns) != len(df_columns):
        raise ValueError(f"csv length:{len(csv_columns)} != df length:{len(df_columns)}")

    csv_set = set(csv_columns)
    df_set = set(df_columns)
    if not (csv_set == df_set):
        errors = []
        for i in range(len(csv_columns)):
            if csv_columns[i] != df_columns[i]:
                errors.append(f"i: {csv_columns[i]} != {df_columns[i]}")
        if len(errors) > 0:
            raise ValueError(",".join(errors))

def make_all_values_match_column_type(df, col, column_type_matcher):
    return df[col].dropna().apply(column_type_matcher).all()

def compute_make_all_values_match_column_type(df, col, column_type_matcher, message, interval_seconds):
    run_with_message(make_all_values_match_column_type, args=(df, col, column_type_matcher), message=message, interval_seconds=interval_seconds)                                          

# process the columns of the DataFrame
# attempting to update the values of each column to match
# their defined column_type, otherwise replace values
# that cannot be converted to None and log the errors
# for the option of future processing

def process_columns(df):
    processed_columns = []
    column_errors = {}
    for col in df.columns:
        column_type = column_types.get(col)
        if column_type is None:
            print(f"Column: '{col}' has no column_type")
            continue
        column_type_extractor = column_type_extractors.get(column_type)
        if column_type_extractor is None:
            print(f"Column: '{col}' has no column_type_extractor")
            continue
        
        def column_type_matcher(x):
            return column_type_extractor(x) is not None
        
        # start the long-running task with a message that displays every interval_seconds
        all_values_match = compute_make_all_values_match_column_type(
            df, col, column_type_matcher, 
            message=f"Checking all values of column: '{col}' for type {column_type}...",
            interval_seconds=2)
        if all_values_match:
            processed_columns.append(col)
            print(f"\nAll non-null values of column: '{col}' are of type {column_type}")
        else:
            # find all unique non-null values that do not match the column type
            non_matching_mask = df[col].dropna().apply(lambda x: not column_type_matcher(x))
            non_matching_unique_values = df[col].dropna()[non_matching_mask].unique()
            n = len(non_matching_unique_values)
            if n > 0:
                error_lines = []
                for v in non_matching_unique_values:
                    error_lines.append(f"Column: {col} Value: {v} does not match column type: {column_type}")
                pre_wrapped = "\n".join(error_lines)
                column_errors[col] = pre_wrapped
                    
        
        # dashed line as run delimiter
        process_columns_logger.info(('-') * 80)
        
        process_columns_logger.info(f"process_columns run started at: {pd.Timestamp.now().isoformat()}")
        process_columns_logger.info("")

        skipped_columns = [col for col in df.columns if col not in column_errors]
        process_columns_logger.info(f"Skipped columns: {skipped_columns}")
        process_columns_logger.info("")
        process_columns_logger.info(f"Processed columns: {processed_columns}")
        for col in column_errors:
            coltype = get_column_type(col)
            errors = column_errors[col]
            num_errors = len(errors)
            process_columns_logger.info(f"Column: [{col}] [{coltype}] has {num_errors} errors")
            for index, error in enumerate(errors):
                wrapped_error = textwrap.fill(f"column: '{col}': error: {index+1}/{num_errors}\n>|{error}|<", width=80)
                process_columns_logger.info("", extra={"pre-wrapped", wrapped_error})
    
        process_columns_logger.info("")
        process_columns_logger.info(f"process_columns run finished at: {pd.Timestamp.now().isoformat()}")
        process_columns_logger.info("")

    process_columns_logger.info("done")

    return df
    

if __name__ == '__main__':
    
    movies_csv = "movies.csv"
    movies_df = pd.read_csv(movies_csv, dtype=str, low_memory=False)
    
    verify_column_names(movies_csv, movies_df)
    
    pairs = [f"{col}:{get_column_dtype(col)}" for col in movies_df.columns]

    print("\n".join(pairs))
        
    process_columns(movies_df)
