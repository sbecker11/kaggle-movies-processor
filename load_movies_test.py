import unittest
import traceback
import sys
import re
import psycopg2
import os
import logging
import json
import csv

from psycopg2 import sql
from dotenv import load_dotenv

from load_movies import get_columns
from load_movies import extract_section_tuples

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("logging with basicConfi...")

# Load environment variables from .env file
load_dotenv()

class TestExtractSectionTuples(unittest.TestCase):
    def _init_(self):
        logging.info("Initializing TestExtractSectionTuples class...")
        pass
    
    def test_extract_dicts(selfl):
        pass
        
    # Retrieve constants from environment variables
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    DB_SCHEMA = os.getenv('DB_SCHEMA')
    MOVIES_CSV_PATH = os.getenv('MOVIES_CSV_PATH')
    MOVIES_CSV_NUM_COLUMNS = int(os.getenv('MOVIES_CSV_NUM_COLUMNS'))

    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    logging.info("Database connection established successfully.")

    cur = conn.cursor()
    cur.execute(sql.SQL("SET search_path TO {schema}").format(schema=sql.Identifier(DB_SCHEMA)))
    conn.commit()
    logging.info("Database schema search path set successfully.")

    def test_with_real_data(self):
        logging.info("Running test_with_real_data function...")

        try:
            column_names = get_columns(self.MOVIES_CSV_PATH)
            
            # Fetch a random rows from the movies table
            limit = 1
            self.cur.execute(f"SELECT * FROM movies ORDER BY RANDOM() LIMIT {limit}")
            logging.info(f"fetching {limit} rows from 'movies' table...")
            rows = self.cur.fetchall()
            
            for row in rows:
                row_dict = dict(zip(column_names, row))
                movie_id = row_dict['id']
                for column_name in ['genres', 'production_companies', 'spoken_languages']:
                    
                    column_value = row_dict[column_name]
                    print(f"column_name: {column_name}")
                    print(f"Orig: column_value:{column_value} movie_id:{movie_id}")
                    results = []
                    function_list = [
                        (extract_section_tuples,(column_value, movie_id))
                    ]
                    for func, args in function_list:
                        try:
                            result = func(*args)
                            print(f"{func.__name__}.input: {column_value}")
                            print(f"{func.__name__}.output: {result}")
                        except Exception as e:
                            print(f"Error in {func.__name__}: {str(e)}")
                            logging.error(traceback.format_exc())
                            raise AssertionError(f"Error in {func.__name__}: {str(e)}")
                        print("Continuing to next function...\n")
                            
        except Exception as e:
            logging.error(traceback.format_exc())
            raise AssertionError(f"Unexpected {type(e).__name__} raised: {str(e)}")
        finally:
            logging.info("test_with_real_data function completed.")


#     def with_contrived_data(self):
#         logging.info("Running test_with_contrived_data function...")

#         try:
#             # Example contrived data
#             column_string = "[{'id':7, 'name': 'bcc \"sldfj\" sl\\x09fjksfdf js'}, {'name': 'example', 'id': 42}, {'id': 3, 'name': 'test'}]"
#             movie_id = 123
            
#             # Expected output
#             expected_output = [
#                 {"id": 7, "name": 'bcc "sldfj" sl\x09fjksfdf js', "movie_id": 123},
#                 {"name": "example", "id": 42, "movie_id": 123},
#                 {"id": 3, "name": "test", "movie_id": 123}
#             ]
            
#             # Call the function
#             result = extract_dicts_1(column_string, movie_id)
            
#             # Check if the result matches the expected output
#             self.assertEqual(result, expected_output, f"Expected {expected_output}, but got {result}")
#         except Exception as e:
#             logging.error(traceback.format_exc())
#             raise AssertionError(f"Unexpected {type(e).__name__} raised: {str(e)}")
#         finally:
#             logging.info("test_with_contrived_data function completed.")


# def extract_dicts_caller():
#     logging.info("Running test_extract_dicts function...")
#     try:
#         # Create an instance of the TestExtractSectionTuples class
#         test = TestExtractSectionTuples()
        
#         # Run the tests
#         test.real_data_test()
#         test.contrived_data_test()
        
#         logging.info("All tests passed successfully.")
#     except Exception as e:
#         logging.error(f"Error during test_extract_dicts: {e}")
#         logging.error(traceback.format_exc())


if __name__ == "__main__":
    unittest.main()

