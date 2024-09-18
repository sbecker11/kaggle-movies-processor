import pandas as pd
import logging

# Configure logging to print to console
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def explore_random_sample(df, sample_size=10, columns=None):
    """
    Randomly sample rows from the DataFrame and display column names followed by actual row data.
    The `columns` argument limits the exploration to the specified columns. If not provided, all columns are used.
    """
    logging.info(f"Exploring a random sample of {sample_size} rows from the dataset.")
    
    # If specific columns are provided, limit the DataFrame to those columns
    if columns:
        df = df[columns]

    # Sample the data
    sampled_df = df.sample(n=sample_size, random_state=42)

    # Output the column names
    print("Column Names:", sampled_df.columns.tolist())

    # Output the sampled rows with their actual row index and string values
    for idx, row in sampled_df.iterrows():
        print(f"Row {idx}:")
        for col in sampled_df.columns:
            print(f"  {col}: {repr(row[col])}")
        print("\n" + "-" * 80 + "\n")  # Separator between rows

def main():
    # Load the movies dataset from the provided Kaggle path
    file_path = '/Users/sbecker11/Downloads/kaggle-movie-data/movies_metadata.csv'
    try:
        # DtypeWarning: Columns (10) have mixed types. 
        # Specify dtype option on import or
        # set low_memory=False.
        df = pd.read_csv(file_path, low_memory=False)

        logging.info(f"Successfully loaded data from {file_path}")
        
        # Output all column names
        print("Loaded columns:", df.columns.tolist())

    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return

    # Specify which columns to explore (with 'id' at the beginning)
    columns_to_explore = ['id', 'genres', 'production_companies', 'original_language']

    # Explore a random sample of 10 rows for data investigation, limited to the specified columns
    explore_random_sample(df, sample_size=10, columns=columns_to_explore)

if __name__ == "__main__":
    main()
