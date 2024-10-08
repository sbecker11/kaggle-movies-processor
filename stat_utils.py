import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from column_types import get_column_type, is_numeric_column, get_column_dtype
from tabulate import tabulate
from string_utils import format_value, print_wrapped_list, Justify

def show_dataframe_stats(df, title=""):
    print(f"{'='*80}")
    if title and len(title.strip()) > 0:
        print(title)
    nrows = len(df)
    print(f"rows: {nrows}")
    print(f"cols: {len(df.columns)}")
    if nrows == 0:
        print("dataframe has zero rows")
        return
    
    # show the first and last 3 rows and columns
    show_df_grid(df, N=3, val_size=8, col_width=10)

    # drop duplicate rows
    print("----before drop_duplicate rows")
    dup_rows_df = find_df_duplicate_rows(df)
    show_df_grid(dup_rows_df, N=3, val_size=8, col_width=10)
    
    df = df.drop(dup_rows_df.index)
    
    print("----after drop_duplicate rows")
    show_df_grid(df, N=3, val_size=8, col_width=10)
        
    # drop columns with more than 85% NaN values
    threshold_perc = 80
    droppable_columns = get_droppable_columns(df, threshold_perc)
    print(f"droppable_columns: {droppable_columns}\n")
    
    print(f"----before dropping {len(droppable_columns)} columns with NaNs > {threshold_perc}%")
    show_df_columns_table(df)
    
    # Drop the specified columns
    df = df.drop(columns=droppable_columns)
    
    print(f"-----after dropping {len(droppable_columns)} columns with NaNs > {threshold_perc}%")
    show_df_columns_table(df)

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
    print(f"DEBUG: first {N} cols: {first_cols}")
    print(f"DEBUG: last {N} cols: {last_cols}")

    # Create a column of dots
    dots_col = pd.Series(['...' for _ in range(len(dff))], name='dots_col')
    dots_col.index = dff.index  # Ensure the index matches

    # Insert the dots column in the middle of the selected columns
    print_wrapped_list(title=f"DEBUG: {len(dff.columns.tolist())} cols before concat dots:",list=dff.columns.to_list())
    dff = pd.concat([dff[first_cols], dots_col, dff[last_cols]], axis=1)
    print_wrapped_list(title=f"DEBUG: {len(dff.columns.tolist())} cols after concat dots:",list=dff.columns.to_list())

    # if this little check is not included, the dots_col 
    # is not found and KeyError will be raised
    _ = True if 'dots_col' in dff.columns else False
    dff.columns.values[N] = '...'
        
    # Update the cols list to include the dots column
    cols = dff.columns.tolist()
    print_wrapped_list(title=f"DEBUG: {len(dff.columns.tolist())} cols after set dots:", list=dff.columns.to_list())

    # Define column alignment (center alignment for all columns)
    # plus one if the showIndex is true
    # format the index values if applicable
    num_cols = len(cols)
    if show_index:
        if isinstance(dff.index, (pd.MultiIndex)):
            raise ValueError("MultiIndex not supported")
        # index values are allowed to take up the entire col_width
        dff.index = dff.index.map(lambda x: format_value(x, col_width, col_width))
        num_cols += 1 # add a column for the index
    
    # Set the column alignment to center for all columns (including the index)
    colalign = ['center'] * num_cols
    
    # get the selected cols from the first N+1 rows
    top_half_df = dff[cols].head(N+1)
    
    # set row N to have dots in all values
    top_half_df.iloc[N] = '...'
    
    # set the index of row N to be empty
    top_half_df.index = top_half_df.index.map(lambda x: ' '*col_width if x == top_half_df.index[N] else x)
    
    # format values only (index values for the entire df are already formatted)
    top_half_df = top_half_df.map(lambda x: format_value(x, val_size, col_width))

    # tabulate top_half_df with column names in header and a dotted row at the bottom
    top_half_table = tabulate(top_half_df, headers='keys', tablefmt='grid', showindex=show_index, colalign=colalign)
    print(top_half_table)

    # get the selected cols of the lasat N rows
    btm_half_df = dff[cols].tail(N)
    
    # format values only (index values for the entire df are already formatted)
    btm_half_df = btm_half_df.map(lambda x: format_value(x, val_size, col_width))

    # tabulate btm_half_df with column names in header 
    btm_half_pre_table = tabulate(btm_half_df, headers='keys', tablefmt='grid', showindex=show_index, colalign=colalign)

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

def show_df_columns_table(df):
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

def get_droppable_columns(df, threshold_perc=75):
    droppable_columns = []
    for col in df.columns:
        nan_percent = get_column_nan_percent(df,col)
        if nan_percent >= threshold_perc:
            droppable_columns.append(col)
    return droppable_columns

def show_column_stats(df, col, title="", max_output_lines=10):
    print(f"{'-'*80}")
    dtype = df[col].dtype
    col_type = get_column_type(col)
    print(f"Column:[{col}] dtype:[{dtype}] column_type[{col_type}]")
    top_col_value_counts = df[col].value_counts()[:max_output_lines]
    print(top_col_value_counts)

    if is_numeric_column(col):
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
        missing_count = df[col].isnan().sum()
        unique_count = df[col].nunique()

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

if __name__ == '__main__':
    df = pd.read_csv("movies.csv")
    
    show_dataframe_stats(df)