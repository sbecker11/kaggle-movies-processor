import pandas as pd
import os
from column_types import process_columns, verify_all_columns_have_extractors

from plot_utils import can_plot_column_distribution, plot_column_distribution
from env_utils import reload_dotenv 
from stat_utils import show_column_stats, get_normalized_df
 
reload_dotenv()

def clean_movies(df):
    # The mother cleaner function that applies all the cleaning functions
    # drops duplicates, blank columns, columns with more than 50% missing values
    # and then applies the process_columns function to cast each column to the
    # appropriate type or None for any values that cannot be cast.
    # The function prints out the number of rows and columns
    # and returns the cleaned and processed DataFrame
    
    print(f"clean_movies starting - rows: {len(df)} columns: {len(df.columns)}")   

    # Drop duplicate rows
    num_duplicates = df.duplicated().sum()
    if num_duplicates > 0:
        indexes_of_duplicate_rows = df[df.duplicated()].index.tolist()
        ids_of_duplicate_rows = df.loc[indexes_of_duplicate_rows, 'id'].tolist()
        print(f"Dropping {num_duplicates} row ids: {ids_of_duplicate_rows}")
        df = df.drop_duplicates()

    print(f"Keeping the first instance of duplicate rows with ids :\n{ids_of_duplicate_rows}")   
    print(f"clean_movies shape after dropping {num_duplicates} duplicate rows - shape: {df.shape()}")   

    # Drop columns that have all null values
    totally_blank_columns = df.columns[df.isnull().all()]
    num_totally_blank_columns = len(totally_blank_columns)
    if num_totally_blank_columns > 0:
        blank_columns = totally_blank_columns.tolist()
        df = df.drop(columns=blank_columns)
        
    print(f"Totally blank columns: {num_totally_blank_columns} with all values missing:\n{blank_columns}") 
    print(f"clean_movies shape after dropping {num_totally_blank_columns} totally blank - shape: {df.shape()}")   

    # Drop columns with more than 50% missing values
    missing_threshold = 0.75
    min_missing = missing_threshold * len(df)
    missing_columns = df.columns[df.isnull().sum() > min_missing] 
    num_missing_columns = len(missing_columns)
    if num_missing_columns > 0:
        df = df.drop(columns=missing_columns)
        
    print(f"Missing columns: {num_missing_columns} with more than {missing_threshold}% missing values:\n{missing_columns}") 
    print(f"clean_movies shape after dropping {num_missing_columns} columns - shape: {df.shape()}") 

    # for each common column type, apply the appropriate extraction function
    # for example, if each value in a column is defined as a float,
    # then the extraction funcion will convert each value to a float
    # or None if conversion is not possible. For example if a given value
    # is a string that cannot be converted to a float then that value 
    # will be replaced with None.
    df = process_columns(df)
    
    # remove blank columns again
    totally_blank_columns = df.columns[df.isnull().all()]
    num_totally_blank_columns = len(totally_blank_columns)
    if num_totally_blank_columns > 0:
        blank_columns = totally_blank_columns.tolist()
        df = df.drop(columns=blank_columns)
        
    print(f"Missing processed columns: {num_missing_columns} with more than {missing_threshold}% missing values:\n{missing_columns}") 
    print(f"clean_movies shape after dropping {num_missing_columns} processed columns - shape: {df.shape()}") 
    
    # Return the cleansed (but not normalized) df for further investigation
    return df

def show_column_stats_and_distribution(df, col, title=""):
    show_column_stats(df, col, title=title)
    if can_plot_column_distribution(df, col):
        input(f"Hit any key to show the distribution of column: '{col}' :")
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
    
    if input("\nReady to review stats and distribution of the raw data? (y/n): ") != 'n':
        for col in df.columns:
            show_column_stats_and_distribution(df, col)
    else:
        print("Skipped review stats and distributions of the raw data.")

    cleaned_df = None
    if input("\nReady to clean (not normalize) the raw data? (y/n): ") != 'n':
        cleaned_df = clean_movies(df)
    else:
        exit("\nSkipped clean (not normalize) the raw dataset. Exiting")

    if cleaned_df is not None:
        if input("\nReady to review stats of the cleaned (not normalized) data? (y/n): ") != 'n':
            for col in df.columns:
                show_column_stats(df, col)
                input("Hit any key to continue")
        else:
            print("\nSkipped review stats of cleaned (not normalized) data")
        
    if cleaned_df is not None:
        if input(f"\nReady to save the cleaned (not normalized) data to {all_cleaned_csv_path}? (y/n): ") != 'n':
            print(f"Saving cleaned df to {all_cleaned_csv_path}")
            df.to_csv(all_cleaned_csv_path, index=False)
        else:
            print("\nSkipped save the cleaned data")

    if cleaned_df is not None:
        norm_df = None
        if input("\nReady to normalize the cleaned data? (y/n): ") != 'n':
            norm_df = get_normalized_df(cleaned_df)
        else:
            exit("\nNormalization not requested. Exiting")

        if input("\nReady to view column stats and distributions of the normalized data? (y/n): ") != 'n':
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