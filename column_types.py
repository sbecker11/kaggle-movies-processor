import json
import pandas as pd
import re
import textwrap
from tee_utils import Tee
import ast
import math

column_errors: dict[str, list[str]] = {}

def save_column_error(column, error):
    # create a new column_errors entry with an empty array
    if column not in column_errors or not isinstance(column_errors[column], list):
        column_errors[column] = []
    column_errors[column].append(error)

def show_all_column_stats(df):
    for col in df.columns:
        show_column_stats(df, col)

def show_column_stats(df, col, title=""):
    print(f"Column: {col} Stats: {title}")
    print(df[col].describe())
    print(f"Number of unique values: {df[col].notnull().nunique()}")
    errors = column_errors.get(col)
    num_errors = 0 if errors is None else len(errors)
    print(f"Column: {col} has {num_errors} extraction errors")
    if num_errors > 0:
        for error in errors:
            print(f"{col}: |{error}|")
    
# process a string, returning None if the string is empty or 'nan
def extract_string(x):
    if x is None:
        return None
    if isinstance(x, str):
        x = x.strip()
        if len(x) > 0:
            if x.lower() == 'nan':
                return None
            return x
    return None

def is_string(s):
    return extract_string(s) is not None

# attempt to extract an integer from a an integer, float or string
# return None if the string is empty or cannot be converted to an integer
def extract_integer(x):
    if x is None:
        return None
    if isinstance(x, str) and len(x.strip()) > 0 and x.strip() == 'NaN':
        return None
    if isinstance(x, int):
        return x
    if isinstance(x, float):
        x = str(x)
    s = extract_string(x)
    if s is not None:
        if s.lower() == 'nan':
            return None

        # if s has a decimal point followed by 1 or more zeros, 
        # remove the decimal point and zeros
        match = re.match(r"(\d+)\.0+", s)
        if match:
            x = match.group(1)
        if x.isdigit():
            try:
                return int(x)
            except ValueError:
                return None
        return None
    return None

def is_integer(s):
    return extract_integer(s) is not None

# extract a float from a float, int or string
def extract_float(x):
    if x is None:
        return None
    if isinstance(x, int):
        return float(x)
    if isinstance(x, float):
        return x
    s = extract_string(x)
    if s is not None:
        if s.lower() == 'nan':
            return None
        try:
            return float(s)
        except ValueError:
            return None
    return None

def is_float(s):
    return extract_float(s) is not None

# extract a boolean from a boolean or a string
def extract_boolean(x):
    if x is None:
        return None
    if isinstance(x, bool):
        return x
    s = extract_string(x)
    if s is not None:
        s = s.strip().lower()
        if s == "true":
            return True
        if s == "false":
            return False
    return None

def is_boolean(s):
    return extract_boolean(s) is not None

# extract a list or a dict from the given string
# or return None if the string has the wrong format
# or cannot be json-parsed
def extract_object(input_str):
    if input_str is None or not isinstance(input_str, str) or len(input_str.strip()) == 0:
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

numeric_column_types = {
    "integer",
    "float"
}
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

def is_numeric_column(col):
    if get_column_type(col) in numeric_column_types:
        return True
    return False

def get_numeric_columns(df):
    return [col for col in df.columns if is_numeric_column(col)]
    
def get_column_type(col):
    column_type = column_types.get(col)
    if column_type is not None:
        return column_type
    else:
        raise ValueError(f"no column type found for column:{col}")
    
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

# Function to change the data type of a column
# def change_column_dtype(df, col):
#     target_dtype = target_dtypes.get(column_types.get(col))
#     if target_dtype is None:
#         print(f"Column: {col} has no target_dtype")
#         return df
#     # Ensure all non-null values match the target data type
#     if target_dtype == 'int':
#         df[col] = df[col].apply(lambda x: int(x) if pd.notna(x) else x)
#     elif target_dtype == 'float':
#         df[col] = df[col].apply(lambda x: float(x) if pd.notna(x) else x)
#     elif target_dtype == 'bool':
#         df[col] = df[col].apply(lambda x: x.strip().lower() == 'true' if pd.notna(x) else x)
#     elif target_dtype == 'str':
#         df[col] = df[col].apply(lambda x: str(x) if pd.notna(x) else x)
    
#     # Change the data type of the column
#     df[col] = df[col].astype(target_dtype)
#     print(f"Changed data type of column: {col} to {target_dtype}")
#     return df

# def is_dtype_numeric(dtype):
#     return dtype in ['int', 'float']

# def get_columns_with_numeric_dtypes(df):
#     numeric_columns = []
#     for col in df.columns:
#         if is_dtype_numeric(df[col].dtype):
#             numeric_columns.append(col)
#     return numeric_columns

# process the columns of the DataFrame
# attempting to replace invalid values with None
# so they can be easily ignored in future processing

def process_columns(df):
    processed_columns = []
    for col in df.columns:
        # for debugging
        # if col == 'production_companies':
        #     pass
        column_type = column_types.get(col)
        if column_type is None:
            print(f"Column: {col} has no column_type")
            continue
        column_type_extractor = column_type_extractors.get(column_type)
        if column_type_extractor is None:
            print(f"Column: {col} has no column_type_extractor")
            continue
        def column_type_matcher(x):
            return column_type_extractor(x) is not None
        all_values_match = df[col].dropna().apply(column_type_matcher).all()
        if all_values_match:
            processed_columns.append(col)
            print(f"\nAll non-null values of column: {col} are of type {column_type}")
        else:
            # find all unique non-null values that do not match the column type
            non_matching_mask = df[col].dropna().apply(lambda x: not column_type_matcher(x))
            non_matching_unique_values = df[col].dropna()[non_matching_mask].unique()
            n = len(non_matching_unique_values)
            if n > 0:
                for v in non_matching_unique_values:
                    save_column_error(col, v)
                    
    column_type_errors_path = "./column_type_errors.txt"
    print("saving column_type errors to:" + column_type_errors_path)         
    with open (column_type_errors_path,"w") as f:
        tee = Tee(f)
        
        # dashed line as run delimiter
        print(('-') * 80, file=tee)
        
        print(f"process_columns run started at: {pd.Timestamp.now().isoformat()}", file=tee)
        print("", file=tee)

        skipped_columns = [col for col in df.columns if col not in column_errors]
        print(f"Skipped columns: {skipped_columns}", file=tee)
        print("", file=tee)
        print(f"Processed columns: {processed_columns}", file=tee)
        for col in column_errors:
            coltype = get_column_type(col)
            errors = column_errors[col]
            num_errors = len(errors)
            print(f"Column: [{col}] [{coltype}] has {num_errors} errors", file=tee)
            for index, error in enumerate(errors):
                wrapped_error = textwrap.fill(f"{col}: error: {index+1}/{num_errors}\n>|{error}|<", width=80)
                print(wrapped_error, file=tee)
                tee.flush()
    
        print("", file=tee)
        print(f"process_columns run finished at: {pd.Timestamp.now().isoformat()}", file=tee)
        print("", file=tee)
        tee.flush()

    print("done")

    return df
    

if __name__ == '__main__':
    
    movies_csv = "movies.csv"
    movies_df = pd.read_csv(movies_csv, dtype=str, low_memory=False)
    
    verify_column_names(movies_csv, movies_df)
    
    pairs = [f"{col}:{get_column_dtype(col)}" for col in movies_df.columns]

    print("\n".join(pairs))
        
    process_columns(movies_df)
