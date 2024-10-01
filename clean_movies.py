import pandas as pd
from dotenv import load_dotenv
import os
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import traceback
import ast

# Load environment variables from .env file
load_dotenv()

# Read the CSV file into a Pandas DataFrame
movies_csv_path = os.getenv('MOVIES_CSV_PATH')
if not movies_csv_path:
    raise ValueError("MOVIES_CSV_PATH environment variable is not set")

# Show a matrix of histograms for pairs of numeric columns
def show_scatter_and_density(df):
    numeric_df = df.select_dtypes(include=[np.number])
    numeric_cols = numeric_df.columns
    num_cols = len(numeric_cols)

    # Create a grid layout
    fig = make_subplots(rows=num_cols, cols=num_cols, 
                        subplot_titles=[
                            f'{x} vs {y}' for x in numeric_cols for y in numeric_cols],
                        shared_xaxes=True, shared_yaxes=True)

    for i, col1 in enumerate(numeric_cols):
        for j, col2 in enumerate(numeric_cols):
            if i == j:
                # Add density plot on the diagonal
                fig.add_trace(go.Histogram(
                    x=numeric_df[col1], nbinsx=20, histnorm='probability density'), row=i + 1, col=j + 1)
            else:
                # Add scatter plot on the off-diagonal
                fig.add_trace(go.Scatter(
                    x=numeric_df[col2], y=numeric_df[col1], mode='markers'), row=i + 1, col=j + 1)

    fig.update_layout(height=800, width=800,
                      title_text="Scatter Plots and Density Plots")
    fig.show()

def show_column_stats(df, col):
    mean = df[col].mean()
    median = df[col].median()
    mode = df[col].mode().iloc[0]
    std_dev = df[col].std()
    skew = df[col].skew()
    kurtosis = df[col].kurtosis()
    z_scores = np.abs(stats.zscore(df[col]))
    min_val = df[col].min()
    max_val = df[col].max()
    range_val = max_val - min_val
    variance = df[col].var()
    iqr = df[col].quantile(0.75) - df[col].quantile(0.25)
    missing_count = df[col].isnull().sum()
    unique_count = df[col].nunique()

    print(f"Column: {col}")
    print(f"  Mean: {mean}")
    print(f"  Median: {median}")
    print(f"  Mode: {mode}")
    print(f"  Standard Deviation: {std_dev}")
    print(f"  Skewness: {skew}")
    print(f"  Kurtosis: {kurtosis}")
    print(f"  Z-scores: {z_scores}")
    print(f"  Minimum: {min_val}")
    print(f"  Maximum: {max_val}")
    print(f"  Range: {range_val}")
    print(f"  Variance: {variance}")
    print(f"  Interquartile Range (IQR): {iqr}")
    print(f"  Missing Values Count: {missing_count}")
    print(f"  Unique Values Count: {unique_count}")

# Compare the effect of different scalers on the data of the given numeric column in the DataFrame
def compare_numeric_scalers(df, col, threshold=3):
    # Step 1: Apply StandardScaler
    standard_scaler = StandardScaler()
    df_standard_scaled = pd.DataFrame(
        standard_scaler.fit_transform(df), columns=df.columns)

    # Step 2: Apply Clamp or Drop Outliers
    df_standard_scaled_clamped = df_standard_scaled.clip(
        lower=-threshold, upper=threshold)
    df_standard_scaled_dropped = df_standard_scaled[(
        df_standard_scaled.abs() <= 3).all(axis=1)]

    # Step 3: Apply MinMaxScaler
    min_max_scaler = MinMaxScaler()
    df_min_max_scaled_clamped = pd.DataFrame(min_max_scaler.fit_transform(
        df_standard_scaled_clamped), columns=df.columns)
    df_min_max_scaled_dropped = pd.DataFrame(min_max_scaler.fit_transform(
        df_standard_scaled_dropped), columns=df.columns)

    # Print results
    show_column_stats(df, col + ' (Original):')
    show_column_stats(df_standard_scaled_clamped, col +
                      " (Standard Scaled Data (Clamped):")
    show_column_stats(df_min_max_scaled_clamped, col +
                      " (MinMax Scaled Data (Clamped):")
    show_column_stats(df_standard_scaled_dropped, col +
                      " (Standard Scaled Data (Dropped):")
    show_column_stats(df_min_max_scaled_dropped, col +
                      " (MinMax Scaled Data (Dropped):")

def is_json_parseable(value):
    try:
        json.loads(value)
        return True
    except (ValueError, TypeError):
        return False

def is_numeric(x):
    if isinstance(x, str) and x.strip() and x.replace('.', '', 1).isdigit():
        return True
    return False

def is_datetime(x):
    if isinstance(x, str):
        try:
            pd.to_datetime(x)
            return True
        except ValueError:
            return False
    return False

def is_boolean(x):
    if isinstance(x, str):
        return x.lower() in ['true', '1', 't', 'y', 'yes']
    return bool(x)

def is_list_with_non_empty_lists(x):
    """
    Check if the input is a string that can be cast to a list containing at least one non-empty list.

    Parameters:
    x (str): The input string to check.

    Returns:
    bool: True if the input can be cast to a list with at 
    least one non-empty list, or one non-empty value, 
    False otherwise.
    
    Tests:
    print(is_list_with_non_empty_lists("[['a', 'b', 'c'], ['d', 'e', 'f']]"))  # Output: True
    print(is_list_with_non_empty_lists("[['a']]"))  # Output: True
    print(is_list_with_non_empty_lists("[['a'], []]"))  # Output: True
    print(is_list_with_non_empty_lists("[]"))  # Output: False
    print(is_list_with_non_empty_lists("[[]]"))  # Output: False
    print(is_list_with_non_empty_lists("[[], [], []]"))  # Output: False
    print(is_list_with_non_empty_lists("['a']"))  # Output: True
    print(is_list_with_non_empty_lists("['a', 'b', 'c']"))  # Output: True
    """
    if isinstance(x, str):
        try:
            result = ast.literal_eval(x)
            if isinstance(result, list) and any((isinstance(item, list) and len(item) > 0) or (not isinstance(item, list) and item) for item in result):
                return True
        except (ValueError, SyntaxError):
            return False
    return False

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

def report_any_columns(df, skip_cols, name, apply_func):
    """
    Reports columns not already in skip_cols 
    that contain ANY values that match the given condition
    and then adds that reported column to the skip_cols list
    so it will not be reported again.
    """
    try:
        any_name_columns = [col for col in df.columns if df[col].apply(apply_func).any() and col not in skip_cols]
        print(f"Columns with ANY {name} values:\n{any_name_columns}")
        for col in any_name_columns:
            num_null = df[col].isnull().sum()
            matching_values = df[col].apply(apply_func)
            num_values = matching_values.sum()
            num_non_values = df[col].apply(lambda x: not apply_func(x)).sum()
            num_all_values = num_null + num_values + num_non_values
            print(f"""
Column {col} with ANY {name} values:
number of null values: {num_null}
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
                print(f"Column: {col} with ANY {name} non_null_values:\n {values_str}")
                
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
    # skip_cols is updated in report_any_columns as each column is processed
    skip_cols = []
    report_any_columns(df, skip_cols, 'boolean', is_boolean)     
    report_any_columns(df, skip_cols, 'datetime', is_datetime)
    report_any_columns(df, skip_cols, 'numeric', is_numeric)
    report_any_columns(df, skip_cols, 'list', is_list_with_non_empty_lists)
    report_any_columns(df, skip_cols, 'dict', lambda x: isinstance(x, dict))
    report_any_columns(df, skip_cols, 'tuple', lambda x: isinstance(x, tuple))
    report_any_columns(df, skip_cols, 'bracket', lambda x: isinstance(x, str) and x.startswith('[') and x.endswith(']'))
    report_any_columns(df, skip_cols, 'braces', lambda x: isinstance(x, str) and x.startswith('{') and x.endswith('}'))
    report_any_columns(df, skip_cols, 'parentheses', lambda x: isinstance(x, str) and x.startswith('(') and x.endswith(')'))
    report_any_columns(df, skip_cols, 'angle_brackets', lambda x: isinstance(x, str) and x.startswith('<') and x.endswith('>'))

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
        df[col] = df[col].map(lambda x: x == 'True')
    for col in df.select_dtypes(include=['datetime']):
        df[col] = pd.to_datetime(df[col])
    for col in df.select_dtypes(include=['number']):
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