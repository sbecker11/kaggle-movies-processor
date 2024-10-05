import pandas as pd
import os
from column_types import process_columns, get_column_type_extractor, get_columns_with_numeric_dtypes
from stat_utils import show_column_stats
from plot_utils import plot_column_distribution
from sklearn.preprocessing import StandardScaler
from env_utils import reload_dotenv 
 
reload_dotenv()

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
  
    # Drop columns with more than 50% missing values
    missing_threshold = 0.5 * len(df)
    missing_columns = df.columns[df.isnull().sum() > missing_threshold] 
    print(f"Dropping columns with more than 50% missing values: {missing_columns}") 
    df = df.drop(columns=missing_columns)

    return df

def clean_movies(df):
    # The mother cleaner function that applies all the cleaning functions
    # and returns the cleaned DataFrame
    
    print(f"clean_movies started with rows: {len(df)} columns: {len(df.columns)}")   

    # for each common column type, apply the appropriate cleaning function
    # for example, if each value in a column is defined as a float,
    # then the cleansing funcion will convert each value to a float
    # or None if conversion is not possible, for example if the value
    # is a string that cannot be converted to a float.
    df = process_columns(df, fix=True)
    
    df = autoscale_numeric_columns(df, verbose=True)
    
    print(f"clean_movies finished with rows: {len(df)} columns: {len(df.columns)}")   

    # Return the cleansed df for further investigation
    return df

def autoscale_numeric_columns(df, verbose=False):
    numeric_columns = get_columns_with_numeric_dtypes(df)
    for col in numeric_columns:
        df = autoscale_numeric_column(df, col, verbose=verbose)            
    return df

def show_column_stats_and_distribution(df, col, title=""):
    stat_utils.show_column_stats(df, col, title=title)
    plot_column_distribution(df, col, title=title)

def autoscale_numeric_column(df, col, verbose=False):
    # use the column type extractor to identify valid values
    # apply StandardScaler to the valid values
    # reinsert the scaled values back into the DataFrame
    # return the DataFrame with the scaled column
    # includes option to show stats and distribution
    # before and after scaling
    
    if verbose:
        title = "Column:{col} stats before scaling"
        show_column_stats_and_distribution(df, col, title=title)
        
    # Get the column type extractor
    column_type_extractor = get_column_type_extractor(col)
    
    # Create a column type matcher which retuns a valid value or None
    def column_type_matcher(x):
        return column_type_extractor(x) is not None
    
    # Create a mask for valid values
    value_mask = df[col].dropna().apply(lambda x: column_type_matcher(x))
    
    # Extract valid values
    valid_values = df[col].dropna()[value_mask]
    
    # Apply StandardScaler to valid values
    scaler = StandardScaler()
    scaled_values = scaler.fit_transform(valid_values.values.reshape(-1, 1))
    
    # Reinsert scaled values back into the DataFrame
    df.loc[valid_values.index, col] = scaled_values
    
    if verbose:
        title = "Column:{col} stats after scaling"
        show_column_stats_and_distribution(df, col, title=title)

    # return the DataFrame with the scaled column
    return df
    

if __name__ == '__main__':
    # Read the CSV file into a Pandas DataFrame
    movies_csv_file = os.getenv('MOVIES_CSV_PATH')
    if not movies_csv_file:
        raise ValueError("MOVIES_CSV_PATH environment variable is not set")

    # the cleaned data goes here
    movie_outputs_path = os.getenv('MOVIES_OUTPUTS_PATH')
    if not movie_outputs_path:
        raise ValueError("MOVIES_OUTPUTS_PATH environment variable is not set")

    pre_cleaned_parquet_path = os.path.join(movie_outputs_path, "pre_cleaned.parquet")
    all_cleaned_csv_path = os.path.join(movie_outputs_path, "all_cleaned.csv")
        
    if os.path.exists(pre_cleaned_parquet_path):
        print(f"Reading from {pre_cleaned_parquet_path}")
        df = pd.read_parquet(pre_cleaned_parquet_path)
    else:
        print(f"Reading from {movies_csv_file} NOT forcing dtype=str")
        df = pd.read_csv(movies_csv_file)
        
        for col in df.columns:
            show_column_stats(df, col)

        # Pre-clean the freshly read data
        df = pre_clean_movies(df)

        print(f"Saving to {pre_cleaned_parquet_path}")
        df.to_parquet(pre_cleaned_parquet_path, index=False)

    df = clean_movies(df)

    choice = input("Save the data (y/n): ")
    if choice == 'y':
        print(f"Saving cleaned df to {all_cleaned_csv_path}")
        df.to_csv(all_cleaned_csv_path, index=False)

    print("done")