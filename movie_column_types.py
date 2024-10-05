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

def fix_quotes_for_json(input_str):
    # Escape embedded apostrophes using a Unicode escape sequence
    # This regular expression targets single quotes that are likely part of the content
    fixed_str = re.sub(r"(?<=\w)'(?=\w)", r'\\u0027', input_str)
    fixed_str = fixed_str.replace("'", '"')
    fixed_str = fixed_str.replace("None", "null")
    try:
        json.loads(fixed_str)
        return fixed_str
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        print(f"Debug Error: {e}")
        print(f"fixed_str: {fixed_str}")
        # If the JSON decoder fails, try to fix the quotes in the JSON string
        # This regular expression targets single quotes that are likely part of the content
        fixed_str = re.sub(r"(?<=\w)'(?=\w)", r'\\u0027', fixed_str)
        try:
            json.loads(fixed_str)
            return fixed_str
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f"Debug Error: {e}")
            print(f"fixed_str: {fixed_str}")
            # If the JSON decoder fails again, return None
            return None
        

def json_load_string(s):
    if s is None:
        return None
    try:
        t = fix_quotes_for_json(s) 
        if t is None:
            return None
        return json.loads(t)
    except (ValueError, TypeError) as e:
        print(f"Error: {e}")
        print(f"Error parsing: {t}")
        return None


# attempt to parse a dict from the given string
def json_load_dict_string(s):
    try:
        result = json_load_string(s)
        if isinstance(result, dict):
            return result
        raise ValueError(f"Expected a dict, got {type(result)}")
    except (ValueError, TypeError) as e:
        print(f"Error: {e}")
        print(f"Error parsing: {s}")
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

def extract_dict(x):
    if x is None or isinstance(x, dict):
        return x
    s = extract_string(x)
    if s is not None:
        try:
            y = json_load_dict_string(s)
            if isinstance(y, dict):
                return y
        except (ValueError, TypeError):
            return None
    return None

def is_dict(x):
    d = extract_dict(x)
    return d is not None


def extract_list_of_dicts(x):
    ## return a list of at least one dict from a string
    ## any of the dicts can be empty
    ## or return None
    if x is None:
        return None
    if isinstance(x, list):
        return x
    # This function should only be called with a string with scquare brackets
    s = extract_string(x)
    if s is None or not s.startswith('[') or not s.endswith(']'):
        return None
        
    list_of_dicts = []
    try:
        y = json_load_string(s)
        if isinstance(y, list):
            if len(y) == 0:
                return None
            for i in y:
                if isinstance(i, dict):
                    list_of_dicts.append(i)
                    continue
                else:
                    ## if any element i is not a dict, return None
                    return None
            if len(list_of_dicts) == 0:
                return None
            return list_of_dicts
    except (ValueError, TypeError) as e:
        print(f"Error: {e}")
        print(f"Error parsing: {s}")
        return None
    return None

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
    "dict": extract_dict,
    "integer": extract_integer,
    "list_of_dicts": extract_list_of_dicts,
    "string": extract_string,
    "float":  extract_float,
    "date": extract_ymd_datetime,
    "status_categories": extract_status_categories
}
target_dtypes = {
    "boolean": "bool",
    "dict": "dict",
    "integer": "int",
    "list_of_dicts": "list",
    "string": "str",
    "float": "float",
    "date": "datetime",
    "status_categories": "str"
}
movie_column_types = {
    "adult": "boolean",
    "belongs_to_collection": "dict",
    "budget": "integer",
    "genres": "list_of_dicts",
    "homepage": "string",
    "id": "integer",
    "imdb_id": "string",
    "original_language": "string",
    "original_title": "string",
    "overview": "string",
    "popularity": "float",
    "poster_path": "string",
    "production_companies": "list_of_dicts",
    "production_countries": "list_of_dicts",
    "release_date": "ymd_date",
    "revenue": "integer",
    "runtime": "float",
    "spoken_languages": "list_of_dicts",
    "status": "status_categories",
    "tagline": "string",
    "title": "string",
    "video": "boolean",
    "vote_average": "float",
    "vote_count": "integer"
}

def get_movie_column_type(col):
    return movie_column_types.get(col)

def get_movie_column_extractor(col):
    return column_type_extractors[movie_column_types.get(col)]

def get_movie_column_type_extractor(movie_column_type):
    return column_type_extractors[movie_column_type]

# Function to change the data type of a column
def change_column_dtype(df, col):
    target_dtype = target_dtypes.get(movie_column_types.get(col))
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

def process_movie_columns(df, fix=False):
    passing_columns = []
    for col in df.columns:
        if col == 'production_companies':
            pass
        movie_column_type = movie_column_types.get(col)
        if movie_column_type is None:
            print(f"Column: {col} has no movie_column_type")
            continue
        column_type_extractor = column_type_extractors.get(movie_column_type)
        if column_type_extractor is None:
            print(f"Column: {col} has no column_type_extractor")
            continue
        def column_type_matcher(x):
            return column_type_extractor(x) is not None
        all_values_match = df[col].dropna().apply(column_type_matcher).all()
        if all_values_match:
            passing_columns.append(col)
            print(f"All non-null values of column: {col} are of type {movie_column_type}")
        else:
            # find all unique non-null values that do not match the column type
            non_matching_mask = df[col].dropna().apply(lambda x: not column_type_matcher(x))
            non_matching_unique_values = df[col].dropna()[non_matching_mask].unique()
            n = len(non_matching_unique_values)
            if n > 0:
                print(f"Column: {col} has {n} non-null values that do not match {movie_column_type}")
                for v in non_matching_unique_values:
                    error = f"|{v}| does not match {movie_column_type} for column: {col}"
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
        print(f"process_movie_columns run at: {run_datetime}", file=tee)
        print(f"Passing columns: {passing_columns}", file=tee)
        for col in column_errors:
            coltype = get_movie_column_type(col)
            dtype = target_dtypes.get(coltype)
            errors = column_errors[col]
            print(f"Column: [{col}] [{coltype}/{dtype}] has {len(errors)} errors", file=tee)
            for index, error in enumerate(errors):
                wrapped_error = textwrap.fill(f"{col}: error: {index} >|{error}|<", width=80)
                print(wrapped_error, file=tee)
                tee.flush()
    

if __name__ == '__main__':
    
    df = pd.read_csv("movies.csv", low_memory=False)
    process_movie_columns(df, fix=False)
