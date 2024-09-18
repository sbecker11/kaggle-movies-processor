import ast
import json
import pandas as pd  # Import pandas for DataFrame operations
import logging

# Finder functions
def is_json_string(val):
    if isinstance(val, str):
        try:
            # Try to parse the JSON string
            parsed_val = json.loads(val)
            # Return True only if it's a JSON object or array
            return isinstance(parsed_val, (dict, list))
        except (ValueError, TypeError, json.JSONDecodeError):
            return False
    return False

def is_json_like_string(val):
    """
    Checks if a given string closely resembles JSON but uses single quotes
    instead of double quotes, which makes it invalid JSON.
    """
    if isinstance(val, str):
        # Regular expression to check if the string resembles JSON but with single quotes
        json_like_pattern = r"^\s*\{[^\{\}]+\}\s*$|^\s*\[[^\[\]]+\]\s*$"
        if re.match(json_like_pattern, val):
            return True
    return False

def is_list_of_tuples(val):
    if isinstance(val, str):
        try:
            # Safely evaluate the string to a Python object
            parsed_val = ast.literal_eval(val)
            # Check if the result is a list
            if isinstance(parsed_val, list):
                # Determine the expected length of tuples (if any)
                expected_length = None
                for item in parsed_val:
                    # Ensure every element is a tuple with at least two elements
                    if not isinstance(item, tuple) or len(item) < 2:
                        return False
                    # Set the expected length based on the first tuple
                    if expected_length is None:
                        expected_length = len(item)
                    # Ensure all tuples have the same length
                    if len(item) != expected_length:
                        return False
                    # Check that all elements in the tuple are of allowed types
                    if not all(isinstance(elem, (int, float, str, bool, type(None), tuple)) for elem in item):
                        return False
                return True
        except (ValueError, SyntaxError):
            # Return False if the string cannot be parsed to a Python object
            return False
    return False

def convert_json_like_to_proper_json(val):
    """
    Converts a JSON-like string (with single quotes) to a valid JSON string (with double quotes).
    """
    if isinstance(val, str):
        # Replace single quotes with double quotes
        return val.replace("'", '"')
    return val

def parse_json_or_json_like_column(df, column_name, apply_json_conversion=False, max_prints=10):
    """
    Parses a column containing JSON or JSON-like strings into a column with corresponding Python objects.
    If `apply_json_conversion` is True, all values in the column will be treated as JSON-like and converted
    before parsing. Reports the row, column, and original value where a value causes a syntax or parse failure.
    """
    parsed_column = []
    error_log = []  # To keep track of errors or syntax issues
    print_count = 0  # Counter to limit the number of prints

    # Apply conversion to the entire column if the column is JSON-like
    if apply_json_conversion:
        df[column_name] = df[column_name].apply(convert_json_like_to_proper_json)

    for idx, item in enumerate(df[column_name]):
        logging.info(f"Row {idx}: Value type before parsing: {type(item)}")

        if isinstance(item, str):
            try:
                # Parse the (possibly corrected) JSON string
                parsed_value = json.loads(item)
                parsed_column.append(parsed_value)
            except (json.JSONDecodeError, ValueError, SyntaxError) as e:
                # Handle any JSON decoding, value, or syntax errors
                parsed_column.append(None)
                error_log.append((idx, column_name, item, str(e)))
                logging.warning(f"Error parsing column '{column_name}' at row {idx}: {item} - {e}")
        else:
            # If it's not a string, mark it as invalid
            parsed_column.append(None)
            error_log.append((idx, column_name, item, "Not a string"))
            logging.warning(f"Error in column '{column_name}' at row {idx}: {item} is not a string.")

    df[column_name] = parsed_column

    # Print up to max_prints errors, each on a new line
    for entry in error_log:
        if print_count < max_prints:
            print(f"Error in column '{entry[1]}' at row {entry[0]}: {entry[2]}\nError message: {entry[3]}")
            print_count += 1
        else:
            print(f"...and {len(error_log) - max_prints} more errors.")
            break

    return df

import json
import re

# if a column is identiifed has having a list of tuples then 
# return all elements as python objects.
# report row and column where a value causes a syntax error or parse failure.
import ast
import logging

def parse_list_of_tuples_column(df, column_name, max_prints=10):
    """
    Parses a column containing strings of lists of tuples into actual lists of tuples.
    Reports the row, column, and original value where a value causes a syntax error.
    """
    parsed_column = []
    error_log = []  # To keep track of replacements or syntax errors
    print_count = 0  # Counter to limit the number of prints

    for idx, item in enumerate(df[column_name]):
        logging.info(f"Row {idx}: Value type before parsing: {type(item)}")

        if isinstance(item, str):
            try:
                # Try to parse the list of tuples using literal_eval
                parsed_value = ast.literal_eval(item)
                parsed_column.append(parsed_value)
            except (ValueError, SyntaxError) as e:
                # Handle cases where the string contains an invalid format or raises a syntax warning
                parsed_column.append(None)
                error_log.append((idx, column_name, item, str(e)))
                logging.warning(f"Error parsing column '{column_name}' at row {idx}: {item} - {e}")
        else:
            parsed_column.append(None)  # Ensure invalid list of tuples are set to None
            error_log.append((idx, column_name, item, "Not a string"))
            logging.warning(f"Error in column '{column_name}' at row {idx}: {item} is not a string.")

    df[column_name] = parsed_column

    # Print up to max_prints errors, each on a new line
    for entry in error_log:
        if print_count < max_prints:
            print(f"Error in column '{entry[1]}' at row {entry[0]}: {entry[2]}\nError message: {entry[3]}")
            print_count += 1
        else:
            print(f"...and {len(error_log) - max_prints} more errors.")
            break

    return df
