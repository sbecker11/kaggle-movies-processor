import pandas as pd
import json
import re
import logging

def replace_internal_double_quotes(val):
    """Replaces internal double quotes with their ISO code."""
    if isinstance(val, str):
        return re.sub(r'(?<!^)(?<!\\)"(?!$)', '\u0022', val)
    return val

def restore_internal_double_quotes(val):
    """Restores ISO code to internal double quotes."""
    if isinstance(val, str):
        return val.replace('\u0022', '"')
    return val

def convert_single_wrapping_quotes_to_double_wrapping_quotes(val):
    """Converts single quotes to double quotes around keys and values."""
    if isinstance(val, str):
        val = re.sub(r"(?<!\\)'([a-zA-Z0-9_]+)'(?=:)", r'"\1"', val)  # Replace single quotes around keys
        val = re.sub(r"(?<=: )'([^']*)'", r'"\1"', val)  # Replace single quotes around values
        return val
    return val

def log_and_replace(df, column_name, idx, original_value, message, max_logged_errors):
    """Logs an error and replaces the value with None."""
    logging.error(f"Error parsing column '{column_name}' at row {idx}: {message}")
    df.at[idx, column_name] = None  # Replace the value with None
    # Append to the bad lines file
    with open('bad_lines.txt', 'a') as f:
        f.write(f"Error parsing column '{column_name}' at row {idx}.\n")
        f.write(f"  Value {original_value} was replaced with None\n")
        f.write(f"  Error message: {message}\n")

def parse_json_like_column(df, column_name, apply_json_conversion=True, max_logged_errors=10):
    """
    Parses a column containing JSON-like strings into Python objects.
    If `apply_json_conversion` is True, all values in the column will be treated as JSON-like and converted.
    
    This function logs row, column, and value causing any syntax or parse failure.
    Limits the number of logged errors to `max_logged_errors`.
    """
    error_count = 0
    replacements = []

    for idx, value in df[column_name].items():
        original_value = value  # Store the original value for logging

        # Check for non-JSON-like values
        if pd.isna(value) or value is None:
            log_and_replace(df, column_name, idx, original_value, "NaN/None is not a valid JSON-like value.", max_logged_errors)
            replacements.append((idx, column_name, original_value))
            continue
        elif isinstance(value, (int, float, bool, bytes, complex)):
            log_and_replace(df, column_name, idx, original_value, f"{value} is not a valid JSON-like value.", max_logged_errors)
            replacements.append((idx, column_name, original_value))
            continue

        try:
            if apply_json_conversion:
                # Apply transformations
                value = replace_internal_double_quotes(value)
                value = convert_single_wrapping_quotes_to_double_wrapping_quotes(value)

                # Parse the JSON-like string
                parsed_value = json.loads(value)  # Attempt to parse as JSON

                # Update the DataFrame with the parsed value
                df.at[idx, column_name] = parsed_value

        except Exception as e:
            error_count += 1
            
            # Log the first N errors
            if max_logged_errors and error_count <= max_logged_errors:
                log_and_replace(df, column_name, idx, original_value, str(e), max_logged_errors)

            # Replace the value with None
            replacements.append((idx, column_name, original_value))  # Record the None replacement
            
    return df, replacements
