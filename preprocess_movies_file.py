import pandas as pd
import logging
from utils import parse_json_like_column

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def clear_bad_lines_file(file_path):
    """Clears the contents of the bad lines file."""
    with open(file_path, 'w') as f:
        f.write('')  # Write an empty string to clear the file

def main(file_path):
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Clear the bad lines file at the start
    bad_lines_file = 'bad_lines.txt'
    clear_bad_lines_file(bad_lines_file)

    # Load the data
    try:
        df = pd.read_csv(file_path)
        logging.info(f"Successfully loaded data from {file_path}")
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        return

    # List of columns to process (from explore_movies_file.py)
    json_like_columns = ['genres', 'production_companies']

    # Process each JSON-like column
    for column_name in json_like_columns:
        df, replacements = parse_json_like_column(df, column_name, apply_json_conversion=True)

        logging.info("")
        logging.info(f"******* {len(replacements)} values were replaced with None in json-like column '{column_name}' *******")
        logging.info("")

        # Log the results for each column
        if replacements:
            for replacement in replacements:
                logging.info(f"  Row {replacement[0]}: {replacement[2]}")  # Log row number and original value

    # Optionally save the processed DataFrame
    output_file = file_path.replace('.csv', '_preprocessed.csv')
    df.to_csv(output_file, index=False)
    logging.info(f"Processed data saved to {output_file}")

if __name__ == "__main__":
    # Specify the path to the CSV file
    kaggle_file = '/Users/sbecker11/Downloads/kaggle-movie-data/movies_metadata.csv'
    main(kaggle_file)
