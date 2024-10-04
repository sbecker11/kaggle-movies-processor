import pandas as pd
import os
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import traceback
import ast

from env_utils import reload_dotenv 
 
reload_dotenv()


# Read the CSV file into a Pandas DataFrame
movies_csv_path = os.getenv('MOVIES_CSV_PATH')
if not movies_csv_path:
    raise ValueError("MOVIES_CSV_PATH environment variable is not set")



# Apply some basic pre-cleaning steps to the raw movies data
def pre_clean_movies(df):
    # Drop duplicate rows
    num_duplicates = df.duplicated().sum()
    if num_duplicates > 0:
        print(f"Dropping duplicate rows: {num_duplicates}")
        df = df.drop_duplicates()
        
    # Drop columns that have all null values
    blank_columns = df.columns[df.isnull().all()]
    print(f"Dropping blank columns: {blank_columns}")
    df = df.drop(columns=blank_columns)
  
    return df

def report_all_columns(df, skip_cols, name, apply_func, valid_values=None):
    """
    Reports columns not already in skip_cols 
    whose non-null values all match the given condition
    defined by the apply_func and then adds that reported 
    column to the skip_cols list
    so it will not be reported again.
    """
    try:
        if valid_values:
            all_name_columns = [
                col for col in df.columns 
                if df[col].dropna().apply(apply_func).all() 
                  and col not in skip_cols 
                  and df[col].dropna().astype(str).str.lower().isin(valid_values).all()
            ]
        else:
            all_name_columns = [
                col for col in df.columns 
                if df[col].dropna().apply(apply_func).all() 
                  and col not in skip_cols 
                  and df[col].dropna()
            ]
            print(f"Columns with ALL {name} values (ignoring nulls): {all_name_columns}") 
            for col in all_name_columns:
                # Filter out null values
                filtered_col = df[col].dropna()
                matching_values = filtered_col.apply(apply_func)
                if valid_values:
                    num_values = filtered_col.str.lower().isin(valid_values).sum()
                else:
                    num_values = matching_values.sum()
                num_non_values = (~matching_values).sum()
                num_all_values = num_values + num_non_values
                print(f"""
Column {col} with ALL {name} values (ignoring nulls) and counting only valid_values:
number of {name} values: {num_values}
number of non-{name} values: {num_non_values}
number of all values: {num_all_values}
""")
            max_view_values = 3
            if num_values > 0:
                # Show the first max_view_values non-null values
                non_null_values = []
                i = 0
                while i < num_values:
                    value = df[col][matching_values].iloc[i]
                    i += 1
                    if pd.isna(value) or (value == 'Unknown'):
                        continue
                    non_null_values.append(value)
                    if len(non_null_values) >= max_view_values:
                        break
                values_str = " ".join(non_null_values)
                print(f"Column: {col} with ALL {name} non_null_values:\n {values_str}")
                
                # Add this col to the skip_cols list so it is not reported again
                skip_cols.append(col)
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())

def explore_movies(df):
    # Reports data statistics without modifying the DataFrame 
    # Assume df has already been cleaned
    
    print(f"explore_movies started with number of rows: {len(df)}")   
    
    # Skip cols that have already been processed
    # skip_cols is updated in report_all_columns as each column is processed
    skip_cols = []
    
    # report_all_columns(df, skip_cols, 'boolean', is_boolean, 
    name = 'boolean'
    all_name_columns = []
    
    for col in df.columns:
        if col in skip_cols:
            continue
        mapping_func = 
        if col not in ['adult', 'original_title', 'production_companies', 'title', 'video']:
            continue
        # drop all null values
        non_null_col = df[col].dropna()
        if non_null_col.empty:
            continue
        # drop all non-name values
        boolean_col = non_null_col.apply(is_boolean)
        filtered_col = non_null_col[boolean_col]
        if filtered_col.empty:
            continue
        all_unique_values = filtered_col.unique()
        if len(all_unique_values) > 2:
            print(f"col:{col} has more than 2 unique values {all_unique_values}")
            continue
        # are all remaining values name values
        all_match_name = filtered_col.all()
        print(f"col:{col} match {name} {all_match_name}")
        if not all_match_name:
            continue
        print(f"col:{col} added to all_name_columns and skip_cols")
        all_name_columns.append(col)
        skip_cols.append(col)
    print(f"Columns with ALL {name} values (ignoring nulls): {all_name_columns}")
    
    
    report_all_columns(df, skip_cols, 'datetime', is_datetime)
    report_all_columns(df, skip_cols, 'numeric', is_numeric)
    report_all_columns(df, skip_cols, 'list', is_list_with_non_empty_lists)
    report_all_columns(df, skip_cols, 'dict', lambda x: isinstance(x, dict))
    report_all_columns(df, skip_cols, 'tuple', lambda x: isinstance(x, tuple))
    report_all_columns(df, skip_cols, 'bracket', lambda x: isinstance(x, str) and x.startswith('[') and x.endswith(']'))
    report_all_columns(df, skip_cols, 'braces', lambda x: isinstance(x, str) and x.startswith('{') and x.endswith('}'))
    report_all_columns(df, skip_cols, 'parentheses', lambda x: isinstance(x, str) and x.startswith('(') and x.endswith(')'))
    report_all_columns(df, skip_cols, 'angle_brackets', lambda x: isinstance(x, str) and x.startswith('<') and x.endswith('>'))

    # See if remaining (non-skip-cols) include any object columns
    categorical_columns = [col for col in df.select_dtypes(include=['object']).columns if col not in skip_cols]
    print(f"Categorical columns: {categorical_columns}")
    
    # See if remaining (non-skip-cols) include any numeric columns
    numeric_columns = [col for col in df.select_dtypes(include=['number']).columns if col not in skip_cols]
    print(f"Numeric columns: {numeric_columns}")
    
    if len(numeric_columns) > 0:
        for col in numeric_columns:
            choice = input(f"compare numeric scalers for column:{col} (y/n): ")
            if choice == 'y':
                compare_numeric_scalers(df, col, threshold=3)

    choice = input(f"show scatter and density plots for all {len(numeric_columns)} numeric columns (y/n): ")
    if choice == 'y':
        show_scatter_and_density(df[numeric_columns])

    print(f"explore_movies finished with number of rows: {len(df)}")   

def clean_movies(df, movies_outputs_path):
    # Returns the cleaned DataFrame
    print(f"clean_movies started with number of rows: {len(df)}")   

    # Drop columns with more than 50% missing values
    missing_threshold = 0.5 * len(df)
    missing_columns = df.columns[df.isnull().sum() > missing_threshold] 
    print(f"Dropping columns with more than 50% missing values: {missing_columns}") 
    df = df.drop(columns=missing_columns)

    # Convert columns to appropriate data types
    for col in df.select_dtypes(include=['bool']):
        print(f"mapping col:{col} to bool")
        df[col] = df[col].map(lambda x: x == 'True')
    for col in df.select_dtypes(include=['datetime']):
        print(f"mapping col:{col} to datetime")
        df[col] = pd.to_datetime(df[col])
    for col in df.select_dtypes(include=['number']):
        print(f"mapping col:{col} to number")
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Find categorical columns
    categorical_columns = df.select_dtypes(include=['object']).columns
    print(f"Categorical columns: {categorical_columns}")
    if len(categorical_columns) > 0:
        # Convert categorical columns to numerical using one-hot encoding
        print(f"Converting categorical columns to numerical using one-hot encoding: {categorical_columns}")
        df = pd.get_dummies(df, columns=categorical_columns)

    def extract_and_join(df, col, pattern):
        """
        Extracts all matches of the given pattern from the specified column,
        unstacks the results, and joins them into a single string for each row.

        Args:
        df (pd.DataFrame): The DataFrame containing the data.
        col (str): The name of the column to process.
        pattern (str): The regex pattern to match.

        Returns:
        pd.Series: A Series with the joined strings for each row.
        """
        return df[col].str.extractall(pattern).unstack().apply(lambda x: ','.join(x.dropna()), axis=1)

    # Map column names to match_column_func and extract_column_funcs
    funcs = [
        # List of comma-separated brace-sections that are enclosed in square brackets: 
        {"match_func": lambda x: x.str.contains(r'\[.*\{.*\}.*\]'), "extract_func": lambda x: x.str.extractall(
            r'\{.*?\}').unstack().apply(lambda x: ','.join(x.dropna()), axis=1)},

        # List of comma-separated parenthesis-sections that are enclosed in square brackets:
        {"match_func": lambda x: x.str.contains(r'\[.*\(.*\).*\]'), "extract_func": lambda x: x.str.extractall(
            r'\(.*?\)').unstack().apply(lambda x: ','.join(x.dropna()), axis=1)},

        # Sequence of comma-separated single-quoted string values that are NOT enclosed in square brackets:
        {"match_func": lambda x: x.str.contains(r"'(.*?)'(,\s*'(.*?)')*"), "extract_func": lambda x: x.str.extractall(
            r"'(.*?)'").unstack().apply(lambda x: ','.join(x.dropna()), axis=1)},

        # Sequence of comma-separated numeric values that are NOT enclosed in square brackets:
        {"match_func": lambda x: x.str.contains(r'\[.*\d+.*\].*'), "extract_func": lambda x: x.str.extractall(
            r'(\d+)').unstack().apply(lambda x: ','.join(x.dropna()), axis=1)},

        # Sequence of comma-separated boolean values that are NOT enclosed in square brackets:
        {"match_func": lambda x: x.str.contains(r'\[.*true|false.*\].*'), "extract_func": lambda x: x.str.extractall(
            r'(true|false)').unstack().apply(lambda x: ','.join(x.dropna()), axis=1)},
    ]

    for col in df.columns:
        for func in funcs:
            if func['match_func'](df[col]):
                movie_col_df = extract_and_join(df, col, func['extract_func'])
                movie_col_path = os.path.join(
                    movie_outputs_path, f'movie_{col}.csv')
                print(f"saving movie_{col}_df number of rows: {len(movie_col_df)} to {movie_col_path}")
                movie_col_df.to_csv(movie_col_path, index=False)
                print(f"dropping column {col} from the DataFrame")
                df = df.drop(columns=[col])
                break

    # Normalize all remaining numeric columns
    for col in df.columns:
        if df[col].dtype == 'number':
            scaler = StandardScaler()
            df[col] = scaler.fit_transform(df[[col]])

    print(f"clean_movies finished with number of rows: {len(df)}")   

    # Return the cleansed df for further investigation
    return df



if __name__ == '__main__':
    movies_csv_file = os.getenv('MOVIES_CSV_PATH')
    if not movies_csv_file:
        raise ValueError("MOVIES_CSV_PATH environment variable is not set")

    movie_outputs_path = os.getenv('MOVIES_OUTPUTS_PATH')
    if not movie_outputs_path:
        raise ValueError("MOVIES_OUTPUTS_PATH environment variable is not set")

    pre_cleaned_parquet = os.path.join(movie_outputs_path, "pre_cleaned.parquet")
    all_cleaned_parquet = os.path.join(movie_outputs_path, "all_cleaned.parquet")
        
    if os.path.exists(pre_cleaned_parquet):
        print(f"Reading from {pre_cleaned_parquet}")
        df = pd.read_parquet(pre_cleaned_parquet)
    else:
        print(f"Reading from {movies_csv_file} forcing dtype=str")
        df = pd.read_csv(movies_csv_file, dtype=str)

        # Pre-clean the freshly read data
        df = pre_clean_movies(df)

        print(f"Saving to {pre_cleaned_parquet}")
        df.to_parquet(pre_cleaned_parquet, index=False)

    explore_movies(df)

    df = clean_movies(df, movie_outputs_path)
    
    df.to_parquet(all_cleaned_parquet, index=False)

    explore_movies(df)

    print("done")