import unittest
import traceback
import psycopg2
import os
import logging

from psycopg2 import sql
from dotenv import load_dotenv

from load_movies import get_columns
from load_movies import extract_section_tuples

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("logging with basicConfi...")

# Load environment variables from .env file
load_dotenv()

class TestExtractSectionTuples(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestExtractSectionTuples, self).__init__(*args, **kwargs)
        logging.info("Initializing TestExtractSectionTuples class...")
        
        # Retrieve constants from environment variables
        self.DB_USER = os.getenv('DB_USER')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD')
        self.DB_HOST = os.getenv('DB_HOST')
        self.DB_PORT = os.getenv('DB_PORT')
        self.DB_NAME = os.getenv('DB_NAME')
        self.DB_SCHEMA = os.getenv('DB_SCHEMA')
        self.MOVIES_CSV_PATH = os.getenv('MOVIES_CSV_PATH')
        self.MOVIES_CSV_NUM_COLUMNS = int(os.getenv('MOVIES_CSV_NUM_COLUMNS'))
    
    def setUp(self):
        logging.info("Setting up TestExtractSectionTuples class...")
        self.conn = psycopg2.connect(
            dbname=self.DB_NAME,
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT
        )
        logging.info("Database connection established successfully.")

        self.cur = self.conn.cursor()
        self.cur.execute(sql.SQL("SET search_path TO {schema}").format(
            schema=sql.Identifier(self.DB_SCHEMA)
        ))
        self.conn.commit()
        logging.info("Database schema search path set successfully.")    

    def tearDown(self):
        logging.info("Tearing down TestExtractSectionTuples class...")
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        logging.info("Database connection closed successfully.")
        
    def test_with_real_data(self):
        logging.info("Running test_with_real_data function...")

        try:
            column_names = get_columns(self.MOVIES_CSV_PATH)
            select_count_query = f"""
                SELECT COUNT(*) FROM {self.DB_SCHEMA}.movies 
                """
            # set up the query but data needs to be fetched
            self.cur.execute(select_count_query)
            row_count = self.cur.fetchone()[0]
            logging.info(f"Total rows in 'movies' table {row_count}")

            limit = 100
            select_query = f"""
                SELECT * FROM {self.DB_SCHEMA}.movies 
                ORDER BY RANDOM() LIMIT {limit}
                """
            self.cur.execute(select_query)

            rows_to_be_read = min(limit, row_count)
            logging.info(f"Fetching {rows_to_be_read} rows from 'movies' table")

            row_count = 0
            while True:
                row = self.cur.fetchone()
                if row is None:
                    logging.info(f"End of rows at row_count: {row_count}")
                    break
 
                # process the row
                row_dict = dict(zip(column_names, row))
                movie_id = row_dict['id']
                for column_name in ['genres', 'production_companies', 'spoken_languages']:
                    try:
                        column_value = row_dict[column_name]
                        logging.info(f"Processing row: {row_count} col: {column_name} value: {column_value}")

                        print(f"column_name: {column_name}")
                        print(f"Orig: column_value:{column_value} movie_id:{movie_id}")
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
                    except KeyError:
                        logging.info(f"KeyError: {column_name} not found in row_dict")
                        continue
                row_count += 1       
            # end of while loop                        

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

