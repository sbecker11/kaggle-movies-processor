import pandas as pd
import os
from column_types import process_columns, verify_all_columns_have_extractors

from plot_utils import plot_column_distribution
from env_utils import reload_dotenv 
from stat_utils import show_column_stats, get_normalized_df
 
reload_dotenv()

def clean_movies(df):
    # The mother cleaner function that applies all the cleaning functions
    # and returns the cleaned DataFrame
    
    print(f"clean_movies starting - rows: {len(df)} columns: {len(df.columns)}")   

    # Drop duplicate rows
    num_duplicates = df.duplicated().sum()
    if num_duplicates > 0:
        indexes_of_duplicate_rows = df[df.duplicated()].index.tolist()
        ids_of_duplicate_rows = df.loc[indexes_of_duplicate_rows, 'id'].tolist()
        print(f"Dropping {num_duplicates} row ids: {ids_of_duplicate_rows}")
        df = df.drop_duplicates()
    
    print(f"clean_movies after dropping {num_duplicates} duplicate rows - rows: {len(df)} columns: {len(df.columns)}")   

    # Drop columns that have all null values
    blank_columns = df.columns[df.isnull().all()]
    print(f"Dropping blank columns: {blank_columns}")
    df = df.drop(columns=blank_columns)
  
    print(f"clean_movies after dropping {len(blank_columns)} blank columns - rows: {len(df)} columns: {len(df.columns)}")   

    # Drop columns with more than 50% missing values
    missing_threshold = 0.5 * len(df)
    missing_columns = df.columns[df.isnull().sum() > missing_threshold] 
    print(f"Dropping columns with more than 50% missing values: {missing_columns}") 
    df = df.drop(columns=missing_columns)

    # for each common column type, apply the appropriate cleaning function
    # for example, if each value in a column is defined as a float,
    # then the cleansing funcion will convert each value to a float
    # or None if conversion is not possible, for example if the value
    # is a string that cannot be converted to a float.
    df = process_columns(df)
        
    print(f"clean_movies finished with rows: {len(df)} columns: {len(df.columns)}")   

    # Return the cleansed df for further investigation
    return df

def show_column_stats_and_distribution(df, col, title=""):
    show_column_stats(df, col, title=title)
    plot_column_distribution(df, col, title=title)

if __name__ == '__main__':
    # Read the CSV file into a Pandas DataFrame
    movies_csv_file = os.getenv('MOVIES_CSV_PATH')
    if not movies_csv_file:
        raise ValueError("MOVIES_CSV_PATH environment variable is not set")

    # the cleaned data goes here
    movie_outputs_path = os.getenv('MOVIES_OUTPUTS_PATH')
    if not movie_outputs_path:
        raise ValueError("MOVIES_OUTPUTS_PATH environment variable is not set")
    all_normalized_csv_path = os.path.join(movie_outputs_path, "all_normalized.csv")
    all_cleaned_csv_path = os.path.join(movie_outputs_path, "all_cleaned.csv")
    
    print(f"Reading from {movies_csv_file} forcing dtype=str")
    df = pd.read_csv("movies.csv", dtype=str, low_memory=False)
    
    # brain check
    verify_all_columns_have_extractors(df)
    
    if input("\nReady to review stats and distribution of initial data? (y/n): ") != 'n':
        for col in df.columns:
            show_column_stats_and_distribution(df, col)
    else:
        print("Skipped review stats and distributions of initial data.")

    cleaned_df = None
    if input("\nReady to clean the dataset? (y/n): ") != 'n':
        cleaned_df = clean_movies(df)
    else:
        print("\nSkipped clean the dataset.")
        print("Exiting")
        exit()

    if cleaned_df is not None:
        if input("\nReady to review stats of cleaned data? (y/n): ") != 'n':
            for col in df.columns:
                show_column_stats(df, col)
        else:
            print("\nSkipped review stats of cleaned data")
        
    if cleaned_df is not None:
        if input(f"\nReady to save the cleaned (not normalized) data to {all_cleaned_csv_path}? (y/n): ") != 'n':
            print(f"Saving cleaned df to {all_cleaned_csv_path}")
            df.to_csv(all_cleaned_csv_path, index=False)
        else:
            print("\nSkipped save the cleaned data")
    else:
        exit("cleaned_df is None. Exiting")

    norm_df = None
    if input("\nReady to normalize the cleaned data? (y/n): ") != 'n':
        norm_df = get_normalized_df(df)
    else:
        exit("no normalization requested. Exiting")

    if input("\nReady to view column stats and distributions of normalized data? (y/n): ") != 'n':
        for col in norm_df.columns:
            show_column_stats_and_distribution(norm_df, col)
    else:
        print("\nSkipped review column stats and distributions of normalized data")
            
    if input(f"\nReady to save the normalized data to {all_normalized_csv_path}? (y/n): ") != 'n':
        print(f"Saving normalized df to {all_normalized_csv_path}")
        norm_df.to_csv(all_normalized_csv_path, index=False)
    else:
        print("\nSkipped save the normalized data")
        
    print("done")