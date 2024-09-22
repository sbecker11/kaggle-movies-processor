import pandas as pd
import re
import json

def escape_internal_quotes(json_str):
    # Use a regular expression to find and escape double quotes within values
    def replace_quotes(match):
        return match.group(1) + match.group(2).replace('"', r'\"') + match.group(3)
    
    # Match double quotes within JSON values
    return re.sub(r'(:\s*")([^"]*?)(")', replace_quotes, json_str)

def preprocess_json_like_column(df, column_name):
    # Replace single quotes with double quotes, but only if the value is a string
    df[column_name] = df[column_name].apply(lambda x: str(x).replace("'", '"') if isinstance(x, str) else x)
    # Escape internal double quotes within the JSON strings but only if it's a string
    df[column_name] = df[column_name].apply(lambda x: escape_internal_quotes(x) if isinstance(x, str) else x)
    return df

def parse_dict_items(json_array_str, row_index):
    def print_bad_dicts(portions):
        for idx, portion in enumerate(portions):
            try:
                json.loads(portion)
            except json.JSONDecodeError:
                print(f"!! Dict {idx + 1} in Row {row_index}: {portion}")

    try:
        items = json.loads(json_array_str)
        if isinstance(items, list):
            print_bad_dicts([json.dumps(item) for item in items])
    except json.JSONDecodeError:
        portions = re.findall(r'\{.*?\}', json_array_str)
        print_bad_dicts(portions)

def parse_single_value(value, row_index):
    try:
        if pd.isna(value) or value.strip() == "":
            return None
        return json.loads(value)
    except json.JSONDecodeError as e:
        if "Expecting property name enclosed in double quotes" in str(e):
            # Use parse_dict_items to identify and print problematic dictionaries
            parse_dict_items(value, row_index)
        return None

def parse_json_like_column(df, column_name, max_errors=10):
    if column_name not in df.columns:
        raise KeyError(f"Column '{column_name}' does not exist in the DataFrame.")
    
    error_count = 0

    def parse_and_count_errors(row):
        nonlocal error_count
        value = row[column_name]
        parsed_value = parse_single_value(value, row.name)
        if parsed_value is None and value.strip() != "":
            error_count += 1
            # Call parse_dict_items to print problematic dictionaries
            parse_dict_items(value, row.name)
            if error_count > max_errors:
                raise ValueError(f"Exceeded maximum number of non-parseable values: {max_errors}")
        return parsed_value

    df[column_name] = df.apply(parse_and_count_errors, axis=1)
    
    return df

def test_regex():
    # Load the data with low_memory=False to avoid DtypeWarning
    df = pd.read_csv('/Users/sbecker11/Downloads/kaggle-movie-data/movies_metadata.csv', low_memory=False)

    # Preprocess the JSON-like column to replace single quotes with double quotes and escape double quotes within values
    df = preprocess_json_like_column(df, 'production_companies')

    # Parse the JSON-like column
    try:
        df = parse_json_like_column(df, 'production_companies', max_errors=20)
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    test_regex()