import pandas as pd
import logging
from utils import parse_json_or_json_like_column, parse_list_of_tuples_column

# Configure logging to print to console
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def explore_random_sample(df, sample_size=20):
    """
    Randomly sample rows from the DataFrame and display column names followed by actual row data.
    This function is for exploring the dataset to investigate the complex data types found in the columns.
    """
    logging.info(f"Exploring a random sample of {sample_size} rows from the dataset.")

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
        df = pd.read_csv(file_path)
        logging.info(f"Successfully loaded data from {file_path}")
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return

    # Explore a random sample of 100 rows for data investigation
    explore_random_sample(df)

    # Column categorization: Define which columns are JSON, JSON-like, or list of tuples
    json_columns = ['belongs_to_collection', 'production_companies', 'production_countries', 'spoken_languages']
    json_like_columns = ['genres']  # Assume this column contains JSON-like strings
    list_of_tuples_columns = ['some_tuple_column']  # Example column for lists of tuples

    # Process JSON columns
    for col in json_columns:
        logging.info(f"Processing JSON column: {col}")
        df = parse_json_or_json_like_column(df, col, apply_json_conversion=False)

    # Process JSON-like columns
    for col in json_like_columns:
        logging.info(f"Processing JSON-like column: {col}")
        df = parse_json_or_json_like_column(df, col, apply_json_conversion=True)

    # Process list of tuples columns
    for col in list_of_tuples_columns:
        logging.info(f"Processing list of tuples column: {col}")
        df = parse_list_of_tuples_column(df, col)

    # Save the processed DataFrame to a new CSV file
    output_file = '/Users/sbecker11/Downloads/kaggle-movie-data/processed_movies_metadata.csv'
    df.to_csv(output_file, index=False)
    logging.info(f"Processed data saved to: {output_file}")

if __name__ == "__main__":
    main()
