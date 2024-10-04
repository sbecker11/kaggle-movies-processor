import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

column_patterns = {
    "adult":"boolean",
    "belongs_to_collection":"single dict of key-value pairs",
    "budget":"float",
    "genres":"list of dict of key-value pairs",
    "homepage":"string",
    "id":"integer",
    "imdb_id":"string",
    "original_language":"string",
    "original_title":"string",
    "overview":"string",
    "popularity":"float",
    "poster_path":"string",
    "production_companies":"list of dicts with key-value-pairs",
    "production_countries":"list of dicts with key-value-pairs",
    "release_date":"date",
    "revenue":"float",
    "runtime":"float",
    "spoken_languages":"list of dicts with key-value-pairs",
    "status":"string categorized",
    "tagline":"string",
    "title":"string",
    "video":"boolean",
    "vote_average":"float",
    "vote_count":"float",
}

movies_csv_path = os.getenv('MOVIES_CSV_PATH')
if not movies_csv_path:
    raise ValueError("MOVIES_CSV_PATH environment variable is not set")

# let all columns choose their own data type
df = pd.read_csv(movies_csv_path,parse_dates=True, 
                 infer_datetime_format=True, 
                 dtype_backend='pyarrow')

# calculate categories from cols with column_pattern string categorized

def get_col_dtype_of_first_non_null_value(df, col):
    i = 0
    while pd.isnull(df[col].iloc[i]):
        i += 1
    return type(df[col].iloc[i])

for col in df.columns:
    print(f"column: '{col}' dtype: '{df[col].dtype}'")
    continue
    if col in column_patterns:
        # compare my column_patterns with the incoming data types
        column_pattern = column_patterns[col]
        if column_pattern == "boolean":
            col_dtype = get_col_dtype_of_first_non_null_value(df, col)
            if not pd.api.types.is_bool_dtype(col_dtype):
                print(f"Column: '{col}' with dtype: '{col_dtype}' does not match pattern: '{column_pattern}'")
        elif column_pattern == "string":
            col_dtype = df[col].dtype
            if not pd.api.types.is_string_dtype(col_dtype):
                print(f"Column: '{col}' with dtype: '{col_dtype}' does not match pattern: '{column_pattern}'")
        elif column_pattern == "float":
            col_dtype = df[col].dtype
            if not pd.api.types.is_float_dtype(col_dtype):
                print(f"Column: '{col}' with dtype: '{col_dtype}' does not match pattern: '{column_pattern}'")
        elif column_pattern == "integer":
            col_dtype = df[col].dtype
            if not pd.api.types.is_integer_dtype(col_dtype):
                print(f"Column: '{col}' with dtype: '{col_dtype}' does not match pattern: '{column_pattern}'")
        elif column_pattern == "date":
            col_dtype = df[col].dtype
            if not pd.api.types.is_datetime64_any_dtype(col_dtype):
                print(f"Column: '{col}' with dtype: '{col_dtype}' does not match pattern: '{column_pattern}'") 
        elif column_pattern == "string categorized":
            unique_category_values = df[col].unique()
            col_dtype = df[col].dtype
            if not pd.api.types.is_string_dtype(col_dtype):
                print(f"Column: '{col}' with dtype: '{col_dtype}' does not match pattern: '{column_pattern}'") 
        elif column_patterns[col] == "single dict of key-value pairs":
            col_dtype =  get_col_dtype_of_first_non_null_value(df, col)
            if not pd.api.types.is_dict_like(col_dtype):
                print(f"Column: '{col}' with dtype: '{col_dtype}' does not match pattern: '{column_pattern}'")
        elif column_patterns[col] == "list of dict of key-value pairs":
            col_dtype = get_col_dtype_of_first_non_null_value(df, col)
            if not pd.api.types.is_list_like(col_dtype):
                print(f"Column: '{col}' with dtype: '{col_dtype}' does not match pattern: '{column_pattern}'")
        elif column_patterns[col] == "dict with key-value-pairs":
            col_dtype = get_col_dtype_of_first_non_null_value(df,col)
            if not pd.api.types.is_dict_like(df[col].iloc[0]):
                print(f"Column: '{col}' with dtype: '{col_dtype}' does not match pattern: '{column_pattern}'")
        elif column_patterns[col] == "list of dicts with key-value-pairs":
            col_dtype = get_col_dtype_of_first_non_null_value(df,col)
            if not pd.api.types.is_list_like(df[col].iloc[0]):
                print(f"Column: '{col}' with dtype: '{col_dtype}' does not match pattern: '{column_pattern}'")
        else:
            raise ValueError(f"Unknown column pattern for column: '{col}'")
    else:
        print(f"column: '{col}' not found in column_patterns")
