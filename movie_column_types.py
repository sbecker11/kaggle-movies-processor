import json
import pandas as pd
import re

def fix_quotes_for_json(s):
    def replace_object(match):
        obj = match.group()
        # Replace quotes for keys
        obj = re.sub(r"'(\w+)':", r'"\1":', obj)
        
        # Replace quotes for values, preserving content
        obj = re.sub(r': \'(.*?)\'', lambda m: f': "{m.group(1)}"', obj)
        
        return obj

    # Pattern to match entire objects
    pattern = r'\{[^{}]*\}'
    
    # Replace quotes in each object
    result = re.sub(pattern, replace_object, s)
    
    # Replace outermost single quotes with square brackets
    result = result.replace("'[", "[").replace("]'", "]")
    
    return result

def test_fix_quotes_for_json():
    # Error: [{"id": 16, "name": "le"Animation'}] != [{"id": 16, "name": "le'Animation"}]
    # Error: [{"id": 16, "name": "Animation with "quotes""}] != [{"id": 16, "name": "Animation with \"quotes\""}]
    errors = 0
    case_a = "[{'id': 16, 'name': 'Animation'}]"
    expected_a = '[{"id": 16, "name": "Animation"}]'
    result_a = fix_quotes_for_json(case_a)
    # '[{"id": 16, "name": "Animation"}]'
    if result_a != expected_a:
        print(f"Error: {result_a} != {expected_a}")
        errors += 1

    case_b = "[{'id': 16, 'name': 'le'Animation'}]"
    expected_b = '[{"id": 16, "name": "le\'Animation"}]'
    result_b = fix_quotes_for_json(case_b)
    # '[{"id": 16, "name": "le"Animation\'}]'
    if result_b != expected_b:
        print(f"Error: {result_b} != {expected_b}")
        errors += 1
    
    case_c = "[{'id': 16, 'name': 'Animation with \"quotes\"'}]"
    expected_c = '[{"id": 16, "name": "Animation with \\"quotes\\""}]'
    result_c = fix_quotes_for_json(case_c)
    # '[{"id": 16, "name": "Animation with "quotes""}]'
    if result_c != expected_c:
        print(f"Error: {result_c} != {expected_c}")
        errors += 1

    if errors > 0:
        return False
    return True

# prepare the string for json.loads
def json_load_string(s):
    if s is None:
        return None
    t = fix_quotes_for_json(s)
    return json.loads(t)

def test_json_load_string():
    s = "[{'id': 16, 'name': 'Animation'}]"
    x = json_load_string(s)
    if x is None:
        print("Error should have returned a list")
        return False
    
    s = "[{'id': 16, 'name': 'le'Animation'}]"
    x = json_load_string(s)
    if x is None:
        print("Error should have returned a list")
        return False
    
    return True

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

def test_extract_integer():
    x = "123"
    if extract_integer(x) is None:
        print("Error should have returned an integer")
        return False
    
    x = "123.14"
    if extract_integer(x) is not None:
        print("Error should have returned None")
        return False
    
    x = "123E-10"
    if extract_integer(x) is not None:
        print("Error should have returned None")
        return False
    
    x = "  "
    if extract_integer(x) is not None:
        print("Error should have returned None")
        return False
    
    x = "123.00000"
    if extract_integer(x) is None:
        print("Error should have not have returned None")
        return False

    return True

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

def test_extract_float():
    x = "3.14"
    if extract_float(x) is None:
        print("Error should have returned a float")
        return False
    x = "3.14.14"
    if extract_float(x) is not None:
        print("Error should have returned None")
        return False
    x = "3.14E-10"
    if extract_float(x) is None:
        print("Error should not have returned None")
        return False
    x = 8.387519
    if extract_float(x) is None:
        print("Error should not have returned None")
        return False

    return True

def extract_boolean(x):
    if x is None:
        return None
    if extract_string(x) is not None:
        return x.strip().lower() in ["true", "false"]
    return False

def test_extract_boolean():
    x = "True"
    if not extract_boolean(x):
        print("Error should have returned True")
        return False
    x = "False"
    if not extract_boolean(x):
        print("Error should have returned True")
        return False
    x = "Falsee"
    if extract_boolean(x):
        print("Error should have returned False")
        return False
    x = None
    if extract_boolean(x):
        print("Error should have returned False")
        return False
    x = "  "
    if extract_boolean(x):
        print("Error should have returned False")
        return False
    return True
    
def extract_dict(x):
    if x is None:
        return None
    if isinstance(x, dict):
        return x
    s = extract_string(x)
    if s is not None:
        try:
            y = json_load_string(s)
            if isinstance(y, dict):
                return y
        except (ValueError, TypeError):
            return None
    return None

def is_dict(x):
    d = extract_dict(x)
    return d is not None

def test_extract_dict():
    x = "{'id': 16, 'name': 'Animation'}"
    y = extract_dict(x)
    if y is None:
        print("Error should have returned a dict")
        return False
    x = "{'id': 16, 'name': 'Animation'"
    y = extract_dict(x)
    if y is not None:
        print("Error should have returned None")
        return False
    x = "{'id': 16, 'name': 'Animation'}"
    y = extract_dict(x)
    if y is None:
        print("Error should have returned a dict")
        return False
    return True 

def extract_list_of_dicts(x):
    ## return a list of at least one dict from a string
    ## any of the dicts can be empty
    ## or return None
    if x is None:
        return None
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

def test_extract_list_of_dicts():
    x = "[{'id': 16, 'name': 'Animation'}, {'id': 35, 'name': 'Comedy'}, {'id': 10751, 'name': 'Family'}]"
    y = extract_list_of_dicts(x)
    if not isinstance(y, list):
        print("Error should have returned a list")
        return False
    
    x = "[{'id': 16, 'name': 'Animation'}, [1,2], 3]"
    y = extract_list_of_dicts(x)
    if y is not None:
        print("Error should have returned None")
        return False
    
    x = "[]"
    y = extract_list_of_dicts(x)
    if y is not None:
        print("Error should have returned None")
        return False
    
    x = "[{'name': 'Yermoliev', 'id': 88753}]"
    y = extract_list_of_dicts(x)
    if y is None:
        print("Error should not have returned None")
        return False
    
    x = '[{"name": "Yermoliev", "id": 88753}]'
    y = extract_list_of_dicts(x)
    if y is None:
        print("Error should not have returned None")
        return False

    x = '[{}]'
    y = extract_list_of_dicts(x)
    if y is None:
        print("Error should not have returned None")
        return False
    
    x = "[{}]"
    y = extract_list_of_dicts(x)
    if y is None:
        print("Error should not have returned None")
        return False

    return True

def extract_status_categories(x):
    if extract_string(x) is not None:
        x = x.strip()
        if x in ["Rumored", "Planned", "In Production", "Post Production", "Released", "Canceled"]:
            return x
    return None

def extract_ymd_date(x):
    if extract_string(x) is not None:
        x = x.strip()
        if len(x) == 10:
            try:
                return pd.to_datetime(x, format="%Y-%m-%d")
            except ValueError:
                return None
    return None

def test_extract_ymd_date():
    x = "2022-10-11"
    y = extract_ymd_date(x)
    if y is None:
        print("Error should have returned a date")
        return False
    x = "2022-10-1"
    y = extract_ymd_date(x)
    if y is not None:
        print("Error should have returned None")
        return False
    x = "2022-10-11T14:14:14.123=06:00"
    y = extract_ymd_date(x)
    if y is not None:
        print("Error should have returned None")
        return False
    return True

column_type_extractors = {
    "boolean": extract_boolean,
    "dict": extract_dict,
    "integer": extract_integer,
    "list_of_dicts": extract_list_of_dicts,
    "string": extract_string,
    "float":  extract_float,
    "date": extract_ymd_date,
    "status_categories": extract_status_categories
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

# usage:
def test_column_types(df):
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
                    print(f"{v} does not match {movie_column_type} for column: {col}")
    

def test_extractors():
    num_passed = 0
    num_tests = 0
    
    num_tests += 1
    if test_fix_quotes_for_json():
        num_passed += 1
        
    num_tests += 1
    if test_json_load_string():
        num_passed +=1
        
    num_tests += 1
    if test_extract_boolean():
        num_passed += 1
        
    num_tests += 1
    if test_extract_integer():
        num_passed += 1
        
    num_tests += 1
    if test_extract_float():
        num_passed += 1
        
    num_tests += 1
    if test_extract_list_of_dicts():
        num_passed += 1
        
    num_tests += 1
    if test_extract_ymd_date():   
        num_passed += 1
        
    num_tests += 1
    if test_extract_dict():
        num_passed += 1
        
    if num_passed == num_tests:
        print("All extractor tests passed.")
        return True
    else:
        print(f"only {num_passed} of {num_tests} tests passed.")
        return False

if __name__ == '__main__':

    test_extractors()
    
    df = pd.read_csv("movies.csv", low_memory=False)
    test_column_types(df)
