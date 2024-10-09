import pandas as pd
import numpy as np
import re
from scipy import stats
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from column_types import get_column_type, is_integer, is_float, is_numeric_column, get_column_dtype, get_column_type_extractor
from tabulate import tabulate
from decorators import char_decoder
from string_utils import format_value, Justify
# from string_utils import print_wrapped_list

TABULATE_CHAR_UNCODED = ' '
TABULETE_CHAR_ENCODED = 'ψ'

def show_dataframe_stats(cdf, title=""):
    print(f"{'='*80}")
    if title and len(title.strip()) > 0:
        print(title)
    nrows = len(cdf)
    print(f"rows: {nrows}")
    print(f"cols: {len(cdf.columns)}")
    if nrows == 0:
        print("dataframe has zero rows")
        return
    
    # show the first and last 3 rows and columns
    show_df_grid(cdf, N=3, val_size=8, col_width=10)

   

def show_duplicates(df):
    
    dups_mask = df.duplicated(subset=['id', 'title'], keep=False)

    # Use the mask and keep the 'id' and 'title' columns of duplicate rows
    df = df.loc[dups_mask, ['id', 'title']]

    # Add the count of rows for each grouping of id
    df['count'] = df.groupby('id')['id'].transform('count')

    # Add a rank column for each grouping of id using the rank method
    df['rank'] = df.groupby('id').cumcount() + 1
    
    # # Keep only rows with rank 1
    df = df[df['rank'] == 1].drop(columns=['rank'])
    
    print("\nkeeping only rows with rank=1 and dropping rank column")
    print(df)

# uses  
# TABULATE_CHAR_ENCODED in place of 
# TABULATE_CHAR_UNCODED to work with
# tabulate_plus which is decorated with @char_decoder
def format_index_value(index_value, idx_size, idx_width):
    # debug break when index_value is an int
    if isinstance(index_value, int):
        pass
    # return a center justified index value with 'char_encoded' for padding
    index_value = format_value(str(index_value).strip(), idx_size, idx_width, justify=Justify.CENTER)
    pattern = r'^(\s*)(\w*)(\s*)$'
    encoder = tabulate_encoder
    def replace_whitespace(match):
        replaced = encoder(match.group(1)) + match.group(2) + encoder(match.group(3))
        return replaced
    index_value = re.sub(pattern, replace_whitespace, str(index_value))
    return index_value

def tabulate_encoder(input_char):
    return input_char.replace(TABULATE_CHAR_UNCODED, TABULETE_CHAR_ENCODED)

@char_decoder(TABULETE_CHAR_ENCODED, TABULATE_CHAR_UNCODED)
def tabulate_plus(*args, **kwargs):
    return tabulate(*args, **kwargs)

# Show the first and last N rows and columns of the DataFrame
# format columns, indexes, and values using val_size and col_width.
# format index values using idx_size and idx_width
def show_df_grid(df, N=5, val_size=8, col_width=10, show_index=True):

    # Make a copy of the DataFrame to avoid modifying the original
    dff = df.copy()
    
    # rename the column names to fit within the specified column width
    cols = dff.columns.tolist()
    for col in dff.columns:
        dff.rename(columns={col: format_value(col, val_size, col_width, justify=Justify.CENTER)}, inplace=True)
    cols = dff.columns.tolist()

    # Select the first N columns and the last N columns
    first_cols = list(dff.columns[:N])
    last_cols = list(dff.columns[-N:])
    # print(f"DEBUG: first {N} cols: {first_cols}")
    # print(f"DEBUG: last {N} cols: {last_cols}")

    # Create a column of dots
    dots_col = pd.Series(['...' for _ in range(len(dff))], name='dots_col')
    dots_col.index = dff.index  # Ensure the index matches

    # Insert the dots column in the middle of the selected columns
    # print_wrapped_list(title=f"DEBUG: {len(dff.columns.tolist())} cols before concat dots:",list=dff.columns.to_list())
    dff = pd.concat([dff[first_cols], dots_col, dff[last_cols]], axis=1)
    # print_wrapped_list(title=f"DEBUG: {len(dff.columns.tolist())} cols after concat dots:",list=dff.columns.to_list())

    # if this little check is not included, the dots_col 
    # is not found and KeyError will be raised
    _ = True if 'dots_col' in dff.columns else False
    dff.columns.values[N] = '...'
        
    # Update the cols list to include the dots column
    cols = dff.columns.tolist()
    # print_wrapped_list(title=f"DEBUG: {len(dff.columns.tolist())} cols after set dots:", list=dff.columns.to_list())

    # Define column alignment (center alignment for all columns)
    # plus one if the showIndex is true
    # format the index values if applicable
    num_cols = len(cols)
    if show_index:
        if isinstance(dff.index, (pd.MultiIndex)):
            raise ValueError("MultiIndex not supported")
        # index values are allowed to take up the entire col_width
        dff.index = dff.index.map(lambda x: format_index_value(x, col_width, col_width))
        num_cols += 1 # add a column for the index
    
    # Set the column alignment to center for all columns (including the index)
    colalign = ['center'] * num_cols
    
    # get the selected cols from the first N+1 rows
    top_half_df = dff[cols].head(N+1)
    
    # set row N to have dots in all values
    top_half_df.iloc[N] = '...'
    
    # set the index of row N to be a string with col_width dashes
    top_half_df.index = top_half_df.index.map(lambda x: '-'*col_width if x == top_half_df.index[N] else x)
    
    # format values only (index values for the entire df are already formatted)
    top_half_df = top_half_df.map(lambda x: format_value(x, val_size, col_width))

    # tabulate top_half_df with column names in header and a dotted row at the bottom
    top_half_table = tabulate_plus(top_half_df, headers='keys', tablefmt='grid', showindex=show_index, colalign=colalign)
    print(top_half_table)

    # get the selected cols of the lasat N rows
    btm_half_df = dff[cols].tail(N)
    
    # format values only (index values for the entire df are already formatted)
    btm_half_df = btm_half_df.map(lambda x: format_value(x, val_size, col_width))

    # tabulate btm_half_df with column names in header 
    btm_half_pre_table = tabulate_plus(btm_half_df, headers='keys', tablefmt='grid', showindex=show_index, colalign=colalign)

    # Remove the header row and the top and bottom divider lines
    btm_half_lines = btm_half_pre_table.split('\n')
    btm_half_table = '\n'.join(btm_half_lines[3:]) 
    print(btm_half_table)

    
def find_df_duplicate_rows(df):
    
    if 'id' not in df.columns or 'title' not in df.columns:
        raise ValueError("DataFrame must contain 'id' and 'title' columns")

    # Find duplicate rows and keep the id and title columns
    dups_mask = df.duplicated(subset=['id', 'title'], keep=False)

    # Use the mask and keep the 'id' and 'title' columns of duplicate rows
    dup_rows_df = df.loc[dups_mask, ['id', 'title']]

    # Use tranform('count') to add a new 'count' with the same value for each row in the group
    # other group tranform methods include: size, sum, mean, std, var, min, max, median, nunique, first, last
    dup_rows_df['count'] = dup_rows_df.groupby('id')['id'].transform('count')

    # Add a rank column for each grouping of id using the cumcount() group method
    # comcount starts at 0, so add 1 to get the rank
    dup_rows_df['rank'] = dup_rows_df.groupby('id').cumcount() + 1

    # Keep only rows with rank 1 and drop the rank
    dup_rows_df = dup_rows_df[dup_rows_df['rank'] == 1].drop(columns=['rank'])
    
    return dup_rows_df

def show_column_value_counts(df, col, max_output_lines, not_null=True):
    try:
        max_line_length = 20
        clean_df_col = df[col]
        if not_null:
            clean_df_col = clean_df_col.dropna()
        top_col_value_counts = clean_df_col.value_counts()[:max_output_lines]
        print(f"Top {max_output_lines} value counts for column: {col}")
        for i, (value, count) in enumerate(top_col_value_counts.items()):
            print(f"{i+1:2}. {value[:max_line_length]} : {count}")
    except KeyError as ke:
        print(f"KeyError: {ke}")

def show_clean_df_columns_table(df):
    # Define column widths
    col_width = 24
    dtype_width = 10
    col_type_width = 20
    unique_cnt_width = 5
    nan_perc_width = 5
    num_cols = 5
    total_width = col_width + dtype_width + col_type_width + unique_cnt_width + nan_perc_width + num_cols
    
    print(f"{'Column':<{col_width}} {'Dtype':<{dtype_width}} {'Column Type':<{col_type_width}} {'Uniques':<{unique_cnt_width}} {'% NaNs':<{nan_perc_width}} ")
    print('-' * total_width)

    for col in df.columns:
        #  natural_dtype = str(df[col].dtype)
        dtype = get_column_dtype(col)
        col_type = get_column_type(col)
        nunique_cnt = df[col].nunique(dropna=True)
        nan_percent = get_column_nan_percent(df, col)
        print(f"{col:<{col_width}} {dtype:<{dtype_width}} {col_type:<{col_type_width}} {nunique_cnt:>{unique_cnt_width}}  {nan_percent:>{nan_perc_width}} ")
    print('-' * total_width)
    print()

def get_dtype_spec(df):
    dtype_spec = {}
    for col in df.columns:
        dtype_spec[col] = get_column_dtype(col)
    return dtype_spec

def get_column_nan_percent(df, col):
    nrows = len(df)
    nan_percent = round(100 * df[col].isna().sum()/nrows)
    return nan_percent

# def get_droppable_columns(df, threshold_perc=75):
#     droppable_columns = []
#     for col in df.columns:
#         nan_percent = get_column_nan_percent(df,col)
#         if nan_percent >= threshold_perc:
#             droppable_columns.append(col)
#     return droppable_columns

def get_prefiltered_df(df):
    percent_threshold = 75
    nan_threshold = percent_threshold * len(df) / 100
    
    # drop duplicate rows
    prefiltered_df = df.drop_duplicates()
    for col in prefiltered_df.columns:
        # drop column if it contains more than 75% NaN values
        if prefiltered_df[col].isna().sum() >= nan_threshold:
            prefiltered_df = prefiltered_df.drop(columns=[col]) 
    return prefiltered_df

# Returns a DataFrame with columns
# that contain only numeric values and
# None for any non-numeric values.
#
# Note that this function should only be used
# on a pre-filtered-df where duoplicate rows
# and mostly-null columns have been dropped.
# 
def get_numeric_df(pre_filtered_df):
    numeric_column_values = {}
    for col in pre_filtered_df.columns:
        if is_numeric_column(col):
            column_type = get_column_type(col)
            column_type_extractor = get_column_type_extractor(column_type)
            numeric_column_series = pre_filtered_df[col].map(column_type_extractor)
            numeric_column_values[col] = numeric_column_series
    numeric_df = pd.DataFrame(numeric_column_values)
    return numeric_df

def get_non_null_numeric_df(numeric_df):
    nnn_column_values = {}
    for col in numeric_df.columns:
        nnn_column_series = numeric_df[col].dropna()
        nnn_column_values[col] = nnn_column_series
    nnn_df = pd.DataFrame(nnn_column_values)
    return nnn_df

def get_clean_numeric_df(df):
    pre_filtered_df = get_prefiltered_df(df)
    numeric_df = get_numeric_df(pre_filtered_df)
    non_null_numeric_df = get_non_null_numeric_df(numeric_df)
    return non_null_numeric_df

# works best with a pre-filtered non-null numeric_dataframe.
# be sure to filter out any null-values in each column
def show_column_stats(df, col, title="", max_output_lines=10, not_null=True):
    print(f"{'-'*80}")
    dtype = df[col].dtype
    col_type = get_column_type(col)
    null_perc = df[col].isna().sum() * 100 / len(df)
    print(f"Column:[{col}] dtype:[{dtype}] column_type[{col_type}] nulls[{null_perc}]%")
    show_column_value_counts(df, col, max_output_lines, not_null)


def show_clean_column_stats(clean_df, col, title="", max_output_lines=10):
    if col not in clean_df.columns:
        raise ValueError(f"Column: {col} not found in clean_df")
        return
    clean_df_col = clean_df[col]
    nan_count = clean_df_col.isna().sum()
    if nan_count > 0:
        ValueError(f"Column: {col} has nan_count: {nan_count} > 0")
        return
    
    show_column_stats(clean_df, col, title="", max_output_lines=10)
    
    mean = clean_df_col.mean()
    median = clean_df_col.median()
    mode = clean_df_col.mode().iloc[0]
    std_dev = clean_df_col.std()
    skew = clean_df_col.skew()
    kurtosis = clean_df_col.kurtosis()
    z_scores = np.abs(stats.zscore(clean_df_col))
    min_val = clean_df_col.min()
    max_val = clean_df_col.max()
    range_val = max_val - min_val
    variance = clean_df_col.var()
    iqr = clean_df_col.quantile(0.75) - clean_df_col.quantile(0.25)
    unique_count = clean_df_col.nunique()

    print("Stats:")
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
    print(f"  Unique Values Count: {unique_count}")

# Compare the effect of different scalers on the data of the given numeric column in the DataFrame
def compare_numeric_scalers(cdf, column_pair,  threshold=3):
    if len(column_pair) != 2:
        ValueError("column_pair must contain two columns")
        return
    col1, col2 = column_pair
    if col1 not in cdf.columns or col2 not in cdf.columns:
        ValueError(f"Column: {col1} or {col2} not found in cdf")
        return
    
    for col in column_pair:
        clean_col_series = cdf[col]
        if clean_col_series.isna().sum() > 0:
            ValueError(f"Column: {col} has nan_count > 0")
            return

    # Step 1: Apply StandardScaler
    standard_scaler = StandardScaler()
    df_standard_scaled = pd.DataFrame(
        standard_scaler.fit_transform(cdf), column_pair)

    # Step 2: Apply Clamp or Drop Outliers
    df_standard_scaled_clamped = df_standard_scaled.clip(
        lower=-threshold, upper=threshold)
    df_standard_scaled_dropped = df_standard_scaled[(
        df_standard_scaled.abs() <= 3).all(axis=1)]

    # Step 3: Apply MinMaxScaler
    min_max_scaler = MinMaxScaler()
    df_min_max_scaled_clamped = pd.DataFrame(min_max_scaler.fit_transform(
        df_standard_scaled_clamped), columns=cdf.columns[column_pair])
    df_min_max_scaled_dropped = pd.DataFrame(min_max_scaler.fit_transform(
        df_standard_scaled_dropped), columns=df.columns[column_pair])

    # Print results
    show_column_stats(cdf, col + ' (Original):')
    show_column_stats(df_standard_scaled_clamped, col +
                      " (Standard Scaled Data (Clamped):")
    show_column_stats(df_min_max_scaled_clamped, col +
                      " (MinMax Scaled Data (Clamped):")
    show_column_stats(df_standard_scaled_dropped, col +
                      " (Standard Scaled Data (Dropped):")
    show_column_stats(df_min_max_scaled_dropped, col +
                      " (MinMax Scaled Data (Dropped):")

if __name__ == '__main__':
    df = pd.read_csv("movies.csv")
    cdf = get_clean_numeric_df(df)
    show_dataframe_stats(cdf)