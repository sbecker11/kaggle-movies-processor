import pandas as pd
import os
from movie_column_types import process_movies, get_movie_column_type, get_movie_column_type_extractor, get_columns_with_numeric_dtypes
from stats_utils import show_column_stats
from plot_utils import show_scatter_and_density, plot_column_distribution


from sklearn.preprocessing import StandardScaler


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


def explore_movies(df):
    # Reports data statistics without modifying the DataFrame 
    # Assume df has already been cleaned
    
    print(f"explore_movies started with number of rows: {len(df)}")   
    process_movies(df, fix=False)
    
    numeric_columns = get_columns_with_numeric_dtypes(df)
    choice = input(f"show scatter and density plots for all {len(numeric_columns)} numeric columns (y/n): ")
    if choice == 'y':
        show_scatter_and_density(df[numeric_columns], title=f"Scatter and Density plots for {len(numeric_columns)} numeric columns")

    print(f"explore_movies finished with number of rows: {len(df)}")   

def clean_movies(df, movies_outputs_path):
    
    # Returns the cleaned DataFrame
    print(f"clean_movies started with number of rows: {len(df)}")   

    # Drop columns with more than 50% missing values
    missing_threshold = 0.5 * len(df)
    missing_columns = df.columns[df.isnull().sum() > missing_threshold] 
    print(f"Dropping columns with more than 50% missing values: {missing_columns}") 
    df = df.drop(columns=missing_columns)

    df = process_movies(df, fix=True)
    
    numeric_columns = get_columns_with_numeric_dtypes(df)
    title = f"scatter and density plots for all {len(numeric_columns)} numeric columns"
    choice = input(f"show {title} before auto-scaling (y/n):")
    if choice == 'y':
        show_scatter_and_density(df[numeric_columns], title=f"{title} before auto-scaling")

    df = auto_scale_numeric_columns(df)
    
    choice = input(f"show {title} after auto-scaling (y/n):")
    if choice == 'y':
        show_scatter_and_density(df[numeric_columns], title=f"{title} after auto-scaling")


    print(f"clean_movies finished with number of rows: {len(df)}")   

    # Return the cleansed df for further investigation
    return df

def auto_scale_numeric_columns(df):
    for col in df.columns:
        if get_movie_column_type(col) in ['float', 'integer']:
            df = scale_valid_values(df, col)
    return df

def column_type_matcher(x, column_type_extractor):
    return column_type_extractor(x) is not None

def scale_valid_values(df, col, show_plots=False):
    
    if show_plots:
        show_column_stats(df, col, title="Before scaling")
        plot_column_distribution(df, col, title="Before scaling")

        
    # Get the column type extractor
    column_type_extractor = get_movie_column_type_extractor(col)
    
    # Create a mask for valid values
    value_mask = df[col].dropna().apply(lambda x: column_type_matcher(x, column_type_extractor))
    
    # Extract valid values
    valid_values = df[col].dropna()[value_mask]
    
    # Apply StandardScaler to valid values
    scaler = StandardScaler()
    scaled_values = scaler.fit_transform(valid_values.values.reshape(-1, 1))
    
    # Reinsert scaled values back into the DataFrame
    df.loc[valid_values.index, col] = scaled_values
    
    if show_plots:
        show_column_stats(df, col, title="After scaling")
        plot_column_distribution(df, col, title="After scaling")

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