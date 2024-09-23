import pandas as pd
import re
import json

def convert_internal_quotes(s):
    # This pattern matches double quotes that are not at the start or end of the string
    pattern = r'(?<!^)"(?!$)'
    return re.sub(pattern, "'", s)

def test_convert_internal_quotes():
    # an array of test cases with input and expected output
    test_frame = [
        ['howdy\"s my name', 'howdy\'s my name'],
        ["I'm a \"string\" with quotes", "I'm a 'string' with quotes"],
        ["", ""],
        ["'single quotes'", "'single quotes'"],
        ["\"double quotes\"", "'double quotes'"]
    ]
    for test in test_frame:
        input, expected = test
        converted = convert_internal_quotes(input)
        print(f"Input:      {input}")
        print(f"Expected:   {expected}")
        print(f"Output:     {converted}")
        if converted == expected:
            print("Test passed")
        else:
            print("Test failed")
            
    
def escape_internal_quotes(s):
    # This pattern matches double quotes that are not 
    # at the start or end of the string and replaces 
    # them with a single quotes
    pattern = r'(?<!^)"(?!$)'
    return re.sub(pattern, "'", s)

def preprocess_json_like_column(df, column_name):
    # Replace single quotes with double quotes, but only if the value is a string
    df[column_name] = df[column_name].apply(lambda x: str(x).replace("'", '"') if isinstance(x, str) else x)
    # Escape internal double quotes within the JSON strings but only if it's a string
    df[column_name] = df[column_name].apply(lambda x: escape_internal_quotes(x) if isinstance(x, str) else x)
    return df

def transform_bad_dict(bad_dict_str, row_index, dict_index):
    # Escape internal double quotes within the bad dictionary string
    transformed_dict = escape_internal_quotes(bad_dict_str)
    print(f"!! Dict {dict_index} in Row {row_index}: {bad_dict_str}")
    print(f"oo Dict {dict_index} in Row {row_index}: {transformed_dict}")
    return transformed_dict

def parse_dict_items(json_array_str, row_index):
    def print_bad_dicts(portions):
        for idx, portion in enumerate(portions):
            try:
                json.loads(portion)
            except json.JSONDecodeError:
                transformed_portion = transform_bad_dict(portion, row_index, idx + 1)
                print(f"?? Dict {idx + 1} in Row {row_index}: {portion}")
                print(f"oo Dict {idx + 1} in Row {row_index}: {transformed_portion}")

    try:
        items = json.loads(json_array_str)
        if isinstance(items, list):
            print_bad_dicts([json.dumps(item) for item in items])
    except json.JSONDecodeError:
        portions = re.findall(r'\{.*?\}', json_array_str)
        print_bad_dicts(portions)

def transform_and_reconstruct(json_array_str, row_index):
    def transform_bad_dicts(portions):
        transformed_portions = []
        for idx, portion in enumerate(portions):
            try:
                json.loads(portion)
                transformed_portions.append(portion)
            except json.JSONDecodeError:
                transformed_portions.append(transform_bad_dict(portion, row_index, idx + 1))
        return transformed_portions

    try:
        items = json.loads(json_array_str)
        if isinstance(items, list):
            transformed_items = transform_bad_dicts([json.dumps(item) for item in items])
            return '[' + ', '.join(transformed_items) + ']'
    except json.JSONDecodeError:
        portions = re.findall(r'\{.*?\}', json_array_str)
        transformed_portions = transform_bad_dicts(portions)
        return '[' + ', '.join(transformed_portions) + ']'

def parse_single_value(value, row_index):
    try:
        if pd.isna(value) or value.strip() == "":
            return None
        return json.loads(value)
    except json.JSONDecodeError as e:
        if "Expecting property name enclosed in double quotes" in str(e):
            # Use parse_dict_items to identify and print problematic dictionaries
            parse_dict_items(value, row_index)
            # Transform and reconstruct the entire value
            return json.loads(transform_and_reconstruct(value, row_index))
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

def test_escape_internal_quotes(input, expected):
    escaped = escape_internal_quotes(input)
    print(f"Input:      {input}")
    print(f"Expected:   {expected}")
    print(f"Output:     {escaped}")
    if escaped == expected:
        print("Test passed")
    else:
        print("Test failed")

def test_parse_single_value():
    def parse_csv_to_json(csv_line):
        # Remove surrounding single quotes if present
        csv_line = csv_line.strip("'")
        
        # Replace single quotes with double quotes for JSON compatibility
        csv_line = csv_line.replace("'", '"')
        
        # Handle escaped single quotes within the data
        csv_line = re.sub(r"(?<!\\)'", "\\'", csv_line)
        
        # Handle double quotes that should be single quotes (like in contractions)
        csv_line = re.sub(r'(?<=\w)"(?=\w)', "'", csv_line)
        
        try:
            # Parse the modified string as JSON
            json_data = json.loads(csv_line)
            return json_data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None

    # Test the function
    test_lines = [
        "[{'Cheated':'gooe'd man'}]",
        "{'Key':'Value with \"quotes\"'}",
        "{'Isn\\'t':'This \"great\"?'}",
        "[{'Multiple':'entries'}, {'in':'one line'}]"
    ]

    for line in test_lines:
        result = parse_csv_to_json(line)
        print(f"Original: {line}")
        print(f"Parsed: {result}")
        print()
     
if __name__ == "__main__":
    # test_escape_internal_quotes('{"name": "Giv\"en Films", "id": 40544}', '{"name": "Giv\'en Films", "id": 40544}')
    # test_escape_internal_quotes('{"name": "Mel\"s Cite du Cinema", "id": 54502}', '{"name": "Mel\'s Cite du Cinema", "id": 54502}')
    
    # test_regex()
    
    test_parse_single_value()