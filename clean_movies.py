import pandas as pd
from dotenv import load_dotenv
import os
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# Load environment variables from .env file
load_dotenv()

# Read the CSV file into a Pandas DataFrame
movies_csv_path = os.getenv('MOVIES_CSV_PATH')
if not movies_csv_path:
    raise ValueError("MOVIES_CSV_PATH environment variable is not set")
df = pd.read_csv(movies_csv_path)

# # Step #1. 
# # Remove rows with duplicate 'id' values

# # Used to hold rows with duplicate 'id' values but different column values
# all_rows_to_be_moved_df = pd.DataFrame(columns=df.columns)

# # Find rows with duplicate 'id' values
# duplicate_ids = df[df.duplicated('id', keep=False)]['id']
# print(f"Number of rows with duplicate 'id' values: {len(duplicate_ids)}")

# # Iterate over each set of duplicate rows
# for id in duplicate_ids.unique():
#     duplicate_rows = df[df['id'] == id]
#     print(f"Number of duplicate rows for id {id}: {len(duplicate_rows)}")

#     # Check if all rows have the same values in all columns
#     if duplicate_rows.drop(columns='id').nunique().sum() == 0:
#         print(f"Dropping duplicate rows for id: {id} with duplicate column values: {len(duplicate_rows)}")
#         df.drop(duplicate_rows.index, inplace=True)
#     else:
#         print(f"Appending duplicate rows for id: {id} with different column values: {len(duplicate_rows)}")
#         all_rows_to_be_moved_df = pd.concat([all_rows_to_be_moved_df, duplicate_rows])

# # Save all_rows_to_be_moved_df to CSV file if it has more than 0 rows
# if not all_rows_to_be_moved_df.empty:
#     all_rows_to_be_moved_df.to_csv('/Users/sbecker11/workspace-dbt/dbt-postgresql/movies_metadata_duplicate_ids.csv', index=False)

# # Drop the duplicate rows from the original DataFrame
# print(f"Number of rows before dropping duplicates: {len(df)}")
# df = df.drop_duplicates(subset='id', keep='first')
# print(f"Number of rows after dropping duplicates: {len(df)}")

# # Step #2: 
# # Find and add zeros to columns with any missing data
# missing_cols = df.columns[df.isna().any()].tolist()
# print(f"Columns with missing data: {missing_cols}")

# # Fill missing values with appropriate zeros
# for col in missing_cols:
#     missing_count = df[col].isna().sum()
#     print(f"Missing data in column {col}: {missing_count}")
    
#     # Determine the appropriate fill value based on column data type
#     fill_value = '0'  # Since all columns are of datatype TEXT
    
#     df[col] = df[col].fillna(fill_value)

# # Step #3: 
# # find and move outier values in each column
# df_outliers = pd.DataFrame()
# for col in df.columns:
#     print(f"Unique values in column {col}: {df[col].unique()}")
#     # use a percentage threshold to identify outliers
#     # calculate threashold by std deviation from mean > 3 std deviations
#     threshold = 3 * df[col].std()
#     mean = df[col].mean()
    
#     # find the outliers in the column
#     outliers_df = df[(df[col] - mean).abs() > threshold]
#     print(f"Outlier values in column {col}: {outliers_df[col]} compared to mean: {mean} and threshold: {threshold}")

#     # at the risk of adding bias to the data, Winsorize the outliers by clamping their distance to the threshold
#     df.loc[(df[col] - mean) > threshold, col] = mean + threshold
#     df.loc[(df[col] - mean) < -threshold, col] = mean - threshold
    
# # Step #4. 
# # find columns that have json-like structured values that have format [{section1},{section2},...,{sectionN}]
# # then flatten the json-like structured values into a new DataFrame with two columns:
# # "movie_id" for the movie_id of that row of the original column value, 
# # and a "section" column that contains the exploded list of sections in the orginal column value for that row.
# # save the new DataFrame to a csv file named movie_{column_name}_sections.csv
# # and then drop the original column from the original DataFrame to avoid redundancy
# for col in df.columns:
#     if df[col].str.contains(r'\[.*\{.*\}.*\]').any():
#         # create a new dataframe for this column and then drop this columrn from ther original dataframe
#         col_df = pd.DataFrame(columns=['movie_id', 'section'])
#         print(f"Column {col} contains json-like structured values")
#         # extract the movie_id from the 'id' column
#         col_df['movie_id'] = df['id']
#         # extract the section values from the column (retain the curly braces)
#         col_df['section'] = df[col].str.extractall(r'\{.*?\}').unstack().apply(lambda x: ','.join(x.dropna()), axis=1)
#         # create the new csv for this column
#         col_df.to_csv(f'/Users/sbecker11/workspace-dbt/dbt-postgresql/movie_{col}_sections.csv', index = False)
#         # drop the original column from the dataframe to avoid redundancy
#         df = df.drop(columns=[col])

 # show a metrix of hiostrams for pairs of numeric columns
def show_scatter_and_density(df):
    numeric_df = df.select_dtypes(include=[np.number])
    numeric_cols = numeric_df.columns
    num_cols = len(numeric_cols)
    
    # Create a grid layout
    fig = make_subplots(rows=num_cols, cols=num_cols, 
                        subplot_titles=[f'{x} vs {y}' for x in numeric_cols for y in numeric_cols],
                        shared_xaxes=True, shared_yaxes=True)
    
    for i, col1 in enumerate(numeric_cols):
        for j, col2 in enumerate(numeric_cols):
            if i == j:
                # Add density plot on the diagonal
                fig.add_trace(go.Histogram(x=numeric_df[col1], nbinsx=20, histnorm='probability density'), row=i+1, col=j+1)
            else:
                # Add scatter plot on the off-diagonal
                fig.add_trace(go.Scatter(x=numeric_df[col2], y=numeric_df[col1], mode='markers'), row=i+1, col=j+1)
    
    fig.update_layout(height=800, width=800, title_text="Scatter Plots and Density Plots")
    fig.show()


def show_column_stats(df, col):
    mean = df.mean()
    median = df.median()
    mode = df.mode().iloc[0]
    std_dev = df.std()
    skew = df.skew()
    kurtosis = df.kurtosis()
    z_scores = np.abs(stats.zscore(df))
    min_val = df[col].min()
    max_val = df[col].max()
    range_val = max_val - min_val
    variance = df[col].var()
    iqr = df[col].quantile(0.75) - df[col].quantile(0.25)
    missing_count = df[col].isnull().sum()
    unique_count = df[col].nunique()

    print(f"Column: {col}")
    print(f"Mean: {mean}")
    print(f"Median: {median}")
    print(f"Mode: {mode}")
    print(f"Standard Deviation: {std_dev}")
    print(f"Skewness: {skew}")
    print(f"Kurtosis: {kurtosis}")
    print(f"Z-scores: {z_scores}")
    print(f"Minimum: {min_val}")
    print(f"Maximum: {max_val}")
    print(f"Range: {range_val}")
    print(f"Variance: {variance}")
    print(f"Interquartile Range (IQR): {iqr}")
    print(f"Missing Values Count: {missing_count}")
    print(f"Unique Values Count: {unique_count}")

# cmopare the effect of different scalers on the data
# of the given numeric column in the DataFrame
def compare_numeric_scalers(df, col, threshold=3):

    # Step 1: Apply StandardScaler
    standard_scaler = StandardScaler()
    df_standard_scaled = pd.DataFrame(standard_scaler.fit_transform(df), columns=df.columns)

    # Step 2: Apply Clamp or Drop Outliers
    df_standard_scaled_clamped = df_standard_scaled.clip(lower=-threshold, upper=threshold)
    df_standard_scaled_dropped = df_standard_scaled[(df_standard_scaled.abs() <= 3).all(axis=1)]

    # Step 3: Apply MinMaxScaler
    min_max_scaler = MinMaxScaler()
    df_min_max_scaled_clamped = pd.DataFrame(min_max_scaler.fit_transform(df_standard_scaled_clamped), columns=df.columns)
    df_min_max_scaled_dropped = pd.DataFrame(min_max_scaler.fit_transform(df_standard_scaled_dropped), columns=df.columns)

    # Print results
    show_column_stats(df, col + ' (Original):')
    show_column_stats(df_standard_scaled_clamped, col + " (Standard Scaled Data (Clamped):")
    show_column_stats(df_min_max_scaled_clamped,  col + " (MinMax Scaled Data (Clamped):")
    show_column_stats(df_standard_scaled_dropped, col + " (Standard Scaled Data (Dropped):")
    show_column_stats(df_min_max_scaled_dropped,  col + " (MinMax Scaled Data (Dropped):")

 def is_json_parseable(value):
    try:
        json.loads(value)
        return True
    except (ValueError, TypeError):
        return False

def generic_cleansing(in_csv_file, cleansed_csv_file):
    # returns the cleaned DataFrame

    # Load the data
    df = pd.read_csv(in_csv_file)

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Drop unnecessary columns
    blank_columns = df.columns[df.isnull().all()]
    print(f"Dropping blank columns: {blank_columns}")
    df = df.drop(columns=blank_columns)
    
    # Drop columns with more than 50% missing values
    missing_threshold = 0.5 * len(df)
    missing_columns = df.columns[df.isnull().sum() > missing_threshold] 
    print(f"Dropping columns with more than 50% missing values: {missing_columns}") 
    df = df.drop(columns=missing_columns)
    
    json_columns = df.columns[df.applymap(is_json_parseable).all()]
    print(f"JSON columns: {json_columns}")
    
    json_list_columns = df.columns[df.applymap(lambda x: isinstance(x, list)).all()]
    print(f"JSON list columns: {json_list_columns}")
    
    json_dict_columns = df.columns[df.applymap(lambda x: isinstance(x, dict)).all()]
    print(f"JSON dict columns: {json_dict_columns}")
    
    json_tuple_columns = df.columns[df.applymap(lambda x: isinstance(x, tuple)).all()]
    print(f"JSON tuple columns: {json_tuple_columns}")
    
    square_brackets_columns = df.columns[df.applymap(lambda x: isinstance(x, str) and x.startswith('[') and x.endswith(']')).all()]
    print(f"Square bracket columns: {square_brackets_columns}")
    
    curly_braced_columns = df.columns[df.applymap(lambda x: isinstance(x, str) and x.startswith('{') and x.endswith('}')).all()]
    print(f"Curly_braced columns: {curly_braced_columns}")

    parentheses_columns = df.columns[df.applymap(lambda x: isinstance(x, str) and x.startswith('(') and x.endswith(')')).all()] 
    print(f"Parentheses columns: {parentheses_columns}")

    # Fill missing values
    df = df.fillna('Unknown')

    # Standardize columns with stringified JSON objcts
    # for col in df.select_dtypes(include=['object']):
    #     df[col] = df[col].str.lower().str.strip()
    # for col in df.select_dtypes(include=['text']):
    #     df[col] = df[col].str.lower().str.strip()
    # Hot-shot columns with boolean values
    
    # Convert columns to appropriate data types
    for col in df.select_dtypes(include=['bool']):
        df[col] = pd.to_bool(df[col], errors='coerce')
    for col in df.select_dtypes(include=['datetime']):
        df[col] = pd.to_datetime(df[col])
    for col in df.select_dtypes(include=['numeric']):
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # find categorical columns
    categorical_columns = df.select_dtypes(include=['object']).columns
    print(f"Categorical columns: {categorical_columns}")
    
    if len(categorical_columns) > 0:
        # Convert categorical columns to numerical using one-hot encoding
        print(f"Converting categorical columns to numerical using one-hot encoding: {categorical_columns}")
        df = pd.get_dummies(df, columns=categorical_columns)


    # Validate data integrity
    # assert df['age'].between(0, 120).all(), "Age values are out of range"

    # Impute missing values with mean
    # df['numeric_column'] = df['numeric_column'].fillna(df['numeric_column'].mean())

    # Save the cleaned data
    df.to_csv(cleansed_csv_file, index=False)
    
    # return the cleansed df for further investigation
    return df


if __name__ == '__main__':
    in_csv_file = os.getenv('IN_CSV_FILE')
    cleansed_csv_file = os.getenv('CLEANSED_CSV_FILE')
    
    df = generic_cleansing(in_csv_file, cleansed_csv_file)
    
    # Show the statistics for all numeric columns
    compare_numeric_scalers(df, threshold=3)

    numeric_df = df.select_dtypes(include=[np.number])
    show_scatter_and_density(numeric_df)
