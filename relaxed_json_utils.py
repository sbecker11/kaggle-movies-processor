import pandas as pd
import demjson3
import io
import re

def advanced_preprocess(json_string):
    def replace_value(match):
        full_match = match.group(0)
        value = match.group(1).strip()
        
        if value.startswith('"') and value.endswith('"'):
            # Already properly quoted, leave it alone
            return full_match
        elif value.startswith("'") and value.endswith("'"):
            # Quoted with single quotes, replace with double quotes
            return ': "' + value[1:-1].replace('"', '\\"') + '"'
        elif re.search(r'["\s\[\]{},:]', value) or value.lower() in ['true', 'false', 'null'] or not value.replace('.', '').isdigit():
            # Contains spaces, special characters, is a keyword, or is not a number, needs quotes
            escaped_value = value.replace('"', '\\"')
            return f': "{escaped_value}"'
        else:
            # Numeric values or already properly formatted
            return full_match

    # Check if the input is a naked string (not starting with { or [)
    if not json_string.strip().startswith(("{", "[")):
        return f'"{json_string.strip()}"'

    # Add quotes to keys if they're not already quoted
    json_string = re.sub(r'(\{|\,)\s*([a-zA-Z0-9_]+)\s*:', r'\1"\2":', json_string)
    
    # Handle values, including those with spaces and internal quotes
    json_string = re.sub(r':\s*(.[^,}\]]*)', replace_value, json_string)
    
    return json_string

def read_relaxed_json(file_or_string):
    if isinstance(file_or_string, str):
        try:
            with open(file_or_string, 'r') as f:
                data = f.read()
        except IOError:
            data = file_or_string
    elif isinstance(file_or_string, io.IOBase):
        data = file_or_string.read()
    else:
        raise ValueError("Input must be a filename, a string, or a file-like object")

    preprocessed_data = advanced_preprocess(data)

    try:
        parsed_data = demjson3.decode(preprocessed_data)
    except demjson3.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Preprocessed data: {preprocessed_data}")
        raise

    if isinstance(parsed_data, (str, int, float, bool)):
        return parsed_data
    elif isinstance(parsed_data, dict):
        return pd.DataFrame([parsed_data])
    elif isinstance(parsed_data, list):
        return pd.DataFrame(parsed_data)
    else:
        return pd.DataFrame([{'value': parsed_data}])
    
def get_detailed_type(obj):
    if isinstance(obj, pd.DataFrame):
        if len(obj) == 0:
            return "Empty DataFrame"
        
        # Check if all column contains lists of dictionaries
        for col in obj.columns:
            if all(isinstance(item, dict) for item in obj[col]):
                return "DataFrame[List(dict)]"
        return "DataFrame"

    elif isinstance(obj, list):
        if not obj:
            return "Empty List"
        # if all element are the same type return List of that type
        if all(isinstance(item, (int, float, str, bool, dict, tuple)) for item in obj):
            return f"List({type(obj[0]).__name__})"
        else:
            return "List[Any]"
    elif isinstance(obj, dict):
        return "Dict"
    else:
        return type(obj).__name__

