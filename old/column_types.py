import json
import pandas as pd
import re
import textwrap
from tee_utils import Tee

column_errors: dict[str, list[str]] = {}

def save_column_error(column, error):
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
    
def get_json_parseable_string(input_str):
    try:
        # see if the input string is already valid JSON
        if json.loads(input_str) is not None:
            return input_str
        
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        print(f"try-except-1 Debug Error: {e}")
        print(f"input_str: {input_str}")
        try:
            # replace single inner quotes iwth encoded-single-quotes
            fixed_str = re.sub(r"(?<=\w)'(?=\w)", r'\\u0027', input_str)
            # replace all remaining single quotes with double quotes
            fixed_str = fixed_str.replace("'", '"')
            # now replace the encoded-single-quotes with escaped single quotes
            fixed_str = fixed_str.replace("\\u0027", "\'")
            # replace python None with JSON null
            fixed_str = fixed_str.replace("None", "null")
            
            if json.loads(fixed_str) is not None:
                return fixed_str

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f"try-except-2 Debug Error: {e}")
            print(f"fixed_str: {fixed_str}")

            # If the JSON decoder fails, try to fix the quotes in the JSON string
            # This regular expression targets single quotes that are likely part of the content
            try:
                fixed_str = re.sub(r"(?<=\w)'(?=\w)", r'\\u0027', fixed_str)
                
                if json.loads(fixed_str) is not None:
                    return fixed_str
                
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                print(f"try-except-3 Debug Error: {e}")
                print(f"fixed_str: {fixed_str}")
                # the given string is simply not parseable
                return None

def extract_string(x):
    if x is None:
        return None
    if isinstance(x, str) and len(x.strip()) > 0:
        return x.strip()
    return None

def extract_integer(x):
    if x is None:
        return None
    if isinstance(x, int):
        return x
    if isinstance(x, float):
        x = str(x)
    # if x has a decimal point followed by 1 or more zeros, 
    # remove the decimal point and zeros
    match = re.match(r"(\d+)\.0+", x)
    if match:
        x = match.group(1)
    if x.isdigit():
        return int(x)
    return None

def extract_float(x):
    if x is None:
        return None
    if isinstance(x, int):
        return float(x)
    if isinstance(x, float):
        return x
    s = extract_string(x)
    if s is not None:
        try:
            return float(s)
        except ValueError:
            return None
    return None

def extract_boolean(x):
    if x is None:
        return None
    if isinstance(x, bool):
        return x
    if extract_string(x) is not None:
        x = x.strip().lower()
        if x == "true":
            return True
        if x == "false":
            return False
    return None

# attempt to extract a list object by 
# using json.loads on the string
# otherwise return None
def extract_dict_string(s):
    if s is None:
        return None
    try:
        y = json.loads(s)
        if isinstance(y, dict):
            return s
        return None
    except (json.JSONDecodeError, ValueError, TypeError):
        return None

def is_dict_string(s):
    y = extract_dict_string(s)
    return y is not None

# Return x if it is a python list object with all 
# elements being python dicts. Otherwise return None
def is_instance_list_of_dict(x):
    return x is not None and isinstance(x, list) and all(isinstance(i, dict) for i in x)

# Returns the given string if it can be parsed
# by json.loads to return a python list of dict
# elements. Otherwise, return None
def extract_list_of_dict_string(s):
    if s is None:
        return None
    try:
        y = json.loads(s)
        if is_instance_list_of_dict(y):
            return s
        return None
    except (json.JSONDecodeError, ValueError, TypeError):
        return None

def is_list_of_dict_string(x):
    y = extract_list_of_dict_string(x)
    return y is not None

def extract_status_categories(x):
    if extract_string(x) is not None:
        x = x.strip()
        if x in ["Rumored", "Planned", "In Production", "Post Production", "Released", "Canceled"]:
            return x
    return None

def extract_ymd_datetime(x):
    if extract_string(x) is not None:
        x = x.strip()
        if len(x) == 10:
            try:
                return pd.to_datetime(x, format="%Y-%m-%d")
            except ValueError:
                return None
    return None

column_type_extractors = {
    "boolean": extract_boolean,
    "dict": extract_dict_string,
    "integer": extract_integer,
    "list_of_dict_string": extract_list_of_dict_string,
    "string": extract_string,
    "float":  extract_float,
    "date": extract_ymd_datetime,
    "status_categories": extract_status_categories
}
target_dtypes = {
    "boolean": "bool",
    "dict": "dict",
    "integer": "int",
    "list_of_dict_string": "list",
    "string": "str",
    "float": "float",
    "date": "datetime",
    "status_categories": "str"
}
column_types = {
    "adult": "boolean",
    "belongs_to_collection": "dict",
    "budget": "integer",
    "genres": "list_of_dict_string",
    "homepage": "string",
    "id": "integer",
    "imdb_id": "string",
    "original_language": "string",
    "original_title": "string",
    "overview": "string",
    "popularity": "float",
    "poster_path": "string",
    "production_companies": "list_of_dict_string",
    "production_countries": "list_of_dict_string",
    "release_date": "ymd_date",
    "revenue": "integer",
    "runtime": "float",
    "spoken_languages": "list_of_dict_string",
    "status": "status_categories",
    "tagline": "string",
    "title": "string",
    "video": "boolean",
    "vote_average": "float",
    "vote_count": "integer"
}

def get_column_type(col):
    return column_types.get(col)

def get_column_extractor(col):
    return column_type_extractors[column_types.get(col)]

def get_column_type_extractor(column_type):
    return column_type_extractors[column_type]

# Function to change the data type of a column
def change_column_dtype(df, col):
    target_dtype = target_dtypes.get(column_types.get(col))
    if target_dtype is None:
        print(f"Column: {col} has no target_dtype")
        return df
    # Ensure all non-null values match the target data type
    if target_dtype == 'int':
        df[col] = df[col].apply(lambda x: int(x) if pd.notna(x) else x)
    elif target_dtype == 'float':
        df[col] = df[col].apply(lambda x: float(x) if pd.notna(x) else x)
    elif target_dtype == 'bool':
        df[col] = df[col].apply(lambda x: x.strip().lower() == 'true' if pd.notna(x) else x)
    elif target_dtype == 'str':
        df[col] = df[col].apply(lambda x: str(x) if pd.notna(x) else x)
    
    # Change the data type of the column
    df[col] = df[col].astype(target_dtype)
    print(f"Changed data type of column: {col} to {target_dtype}")
    return df

def is_dtype_numeric(dtype):
    return dtype in ['int', 'float']

def get_columns_with_numeric_dtypes(df):
    numeric_columns = []
    for col in df.columns:
        if is_dtype_numeric(df[col].dtype):
            numeric_columns.append(col)
    return numeric_columns

# process the columns of the DataFrame
# if fix is true, then replace invalid values with None
# so they can be easily ignored in future processing

def process_columns(df, fix=False):
    passing_columns = []
    for col in df.columns:
        if col == 'production_companies':
            pass
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
            passing_columns.append(col)
            print(f"All non-null values of column: {col} are of type {column_type}")
        else:
            # find all unique non-null values that do not match the column type
            non_matching_mask = df[col].dropna().apply(lambda x: not column_type_matcher(x))
            non_matching_unique_values = df[col].dropna()[non_matching_mask].unique()
            n = len(non_matching_unique_values)
            if n > 0:
                print(f"Column: {col} has {n} non-null values that do not match {column_type}")
                for v in non_matching_unique_values:
                    error = f"|{v}| does not match {column_type} for column: {col}"
                    print(error)
                    save_column_error(col, error)
                if fix:
                    print(f"Fixing {n} values for column: {col}")
                    df.loc[non_matching_mask, col] = None
            if fix:
                change_column_dtype(df, col)

    output_column_errors_path = "./movie_outputs.column_errors.txt"
    with open (output_column_errors_path,"a") as f:
        tee = Tee(f)
        
        # outputting a dashed line to separate the output 
        # of this run
        run_datetime = pd.Timestamp.now().isoformat()
        dashed_line = ('-') * 80
        print(dashed_line, file=tee)
        print(f"process_columns run at: {run_datetime}", file=tee)
        print(f"Passing columns: {passing_columns}", file=tee)
        for col in column_errors:
            coltype = get_column_type(col)
            dtype = target_dtypes.get(coltype)
            errors = column_errors[col]
            print(f"Column: [{col}] [{coltype}/{dtype}] has {len(errors)} errors", file=tee)
            for index, error in enumerate(errors):
                wrapped_error = textwrap.fill(f"{col}: error: {index} >|{error}|<", width=80)
                print(wrapped_error, file=tee)
                tee.flush()
    

if __name__ == '__main__':
    
    df = pd.read_csv("movies.csv", low_memory=False)
    process_columns(df, fix=False)
