import psycopg2
from psycopg2 import sql
import logging
import traceback
import json
import re
from dotenv import load_dotenv
import os
import sys
import csv
import unittest


# Load environment variables from .env file
load_dotenv()

# Retrieve constants from environment variables
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_SCHEMA = os.getenv('DB_SCHEMA')
MOVIES_CSV_PATH = os.getenv('MOVIES_CSV_PATH')
MOVIES_CSV_NUM_COLUMNS = int(os.getenv('MOVIES_CSV_NUM_COLUMNS'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import re
import json

def find_curly_braced_sections_separated_by_comma(column_string):
    # return a list of all curly-braced sections separated by commas
    # in the given column string, or an empty list if the column string
    # does not contain any valid curly-braced sections separated by commas
    
    # Define the pattern to match curly-braced sections separated by commas
    pattern = r'\{.*?\}(?=,|\s*$)'
    
    # Find all matches of the pattern in the column string
    matches = re.findall(pattern, column_string)
    
    # Check if the matches are correctly separated by commas
    for i in range(len(matches) - 1):
        if not column_string[column_string.find(matches[i]) + len(matches[i])] == ',':
            return []
        
    # return the matches if they are correctly separated by commas
    return matches

def is_quote_wrapped_not_empty(v_str):
    # returnr True if the given string value v_str 
    # is not empty and is wrapped with matching 
    # single or double quotes
    q = v_str[0]
    return (len(v_str) > 0) and (v_str[0] in ["'", '"']) and (v_str[-1] == q)

def is_quote_wrapped(v_str):
    # returnr True if the given string value v_str 
    # is wrapped with matching single or double quotes
    q = v_str[0]
    return (q in ["'", '"']) and (v_str[-1] == q)

def is_quote_wrapped_not_empty(v_str):
    return len(v_str) > 0 and is_quote_wrapped(v_str)

def get_double_quote_wrapped_value(v_str) :
    # remove all wrapping quotes until none left
    # and return the value wrapped with double quotes
    while is_quote_wrapped(v_str):
        v_str = v_str[1:-1]
    return f'"{v_str}"'

def str_to_value(v_str):
    # convert the string value v_str to the correct type
    # if it is a string, then ensure it is wrapped with
    # single or double quotes
    if is_quote_wrapped_not_empty(v_str):
        return v_str
    if v_str == "True":
        return True
    elif v_str == "False":
        return False
    elif v_str.isdigit():
        return int(v_str)
    elif re.match(r'^-?\d+(?:\.\d+)?$', v_str):
        return float(v_str)
    logging.info(f"Value is not a string or a valid type: {v_str}")
    return None


def extract_section_tuples(column_string, movie_id):
    """
    aAsample column_string with 3 curly-braced sections separated by commas:
    
    [{'name': 'TriStar Pictures', 'id': 559}, {'name': "Teitler's Film", 'id': 2550}, {'name': "Int\xe6rscope's Communi\x01d8tions", 'id': 10201}]

    Note that 
    the value of the 1st curly-braced section contains no internal quotes or escaped unicode characters.
    the value of the 2nd curly-braced section contains an internal quote that is not escaped.
    the value of the 3rd curly-braced section contains an internal quote and two unicodes that are escaped.
    the keys of all 3 curly-braced sections are wrapped with single quotes.
    the non-string valus are not wrapped with quotes.
    the final value of all 3 curly-braced sections are wrapped with double quotes.
    
    This function returns a list of valid key-value tuples extracted from
    the given column string. Each tuple has 3 key-value 
    pairs with keys 'id', 'name', and 'movie_id' using the
    passed in movie_id as its value. 
    
    If all 3 found tuples are valid, function should return a list 
    of all valid 3-tuples extracted with the movie_id added as the
    third key-value pair in each tuple.
    [
        ('name': "TriStar Pictures", 'id': 559, 'movie_id', 123),
        ('name': "Teitler's Film", 'id': 2550, 'movie_id', 123), 
        ('name': "Intærscope's Commǘnications", 'id': 10201, 'movie_id', 123)
    ]
    
    Raise an Exception if non-recoverale error is encountered.
    """
    # check for valid movie_id
    if movie_id is None:
        raise Exception("Movie_id is None.")
    # same for all tuples
    movie_key_value_pair = ('movie_id', movie_id)  
    
    # Ensure column_string is a string
    if not isinstance(column_string, str) or len(column_string) == 0:
        raise Exception(f"Column string is empty or not a string: {original_column_string}")

    # ensure the column string is wrapped with square brakets
    if not column_string.startswith("[") or not column_string.endswith("]"):
        raise Exception(f"Column string is not wrapped with square brackets: {original_column_string}")
    
    # save fpr logging
    original_column_string = column_string

    # remove the wrapping square brackets
    column_string = column_string.strip().strip("[]")
    
    if len(column_string) == 0:
        raise Exception(f"Column string is empty: {original_column_string}")
        
    # Ensure it contains "id" and "name" keys
    if 'id' not in column_string or 'name' not in column_string:
        raise Exception(f"Column string does not contain 'id' and 'name' keys: {original_column_string}")
    
    # each curly-braced section should yield a section tuple with keys 
    # id, name, and movie_id
    all_section_tuples = []
    try:
        # each curly-braced section is separated by a comma
        curly_braced_sections = find_curly_braced_sections_separated_by_comma(column_string)

        # extract two comma-separated key-value pairs from each curly-braced section
        # each section should contain two key-value pairs to create a valid section_tuple
        # Regular expression to match key-value pairs
        pattern = re.compile(r"(['\"]?\w+['\"]?):\s*(.*)")
        for curly_braced_section in curly_braced_sections:
            # e.g. curly_braced_section = {"'id': 53, 'name': 'Thr'iller'"}
            
            # remove wrapping curly braces
            section = curly_braced_section.strip().strip("{}")
            # e.g. section = "'id': 53, 'name': 'Thr'iller'" 

            parts = re.split(r",\s*", section) # split by comma and optional space
            # e.g. parts = ["'id': 53", "'name': 'Thr'iller'"]
            
            key_value_pairs = []
            for part in parts:
                # e.g. part = "'id': 53" or "'name': 'Thr'iller'"
                match = pattern.match(part)
                if match:
                    key, value = match.groups()
                    # e.g. key = "'id'", value = "53"   or key = "'name'", value = "'Thr'iller'"
                    key_value_pairs.append((key, value))
                    # e.g. key_value_pairs = [("'id'", "53")] or [("'name'", "'Thr'iller'")]
                else:
                    logging.info(f"Part does not match pattern: {part}")
                    continue # to the next part
            # end of for part loop
            if len(key_value_pairs) != 2:
                logging.info(f"Section does not contain two key-value pairs: {curly_braced_section} so skipping.")
                continue # skip to next section
            # traverse both key-value pairs
            for i in range(2):
                key = key_value_pairs[i][0]
                key = get_double_quote_wrapped_value(key)
                value = key_value_pairs[i][1]
                value = str_to_value(value)
                if value is None:
                    logging.info(f"Value is not a valid type: {value} so skipping")
                    continue # skip to next section
                key_value_pairs[i] = (key, value)
                
            # end of for i loop
            if len(key_value_pairs) != 2:
                logging.info(f"Section does not contain two valid key-value pairs: {curly_braced_section}")
                continue # to next section
            
            # create the section_tuple from the two key_value_pars and the movie_key_value_pair
            section_tuple = (key_value_pairs[0], key_value_pairs[1], movie_key_value_pair)
            all_section_tuples.append(section_tuple)
        # end of curly-braced sections loop
        if len(all_section_tuples) == 0:
            logging.info(f"No valid section_tuples found for column string: {original_column_string}") 
            return []
                                                   
        logging.info(f"Returning {len(all_section_tuples)} valid section_tuples for column string: {original_column_string}")
        return all_section_tuples

    except Exception as e:
        logging.error(traceback.format_exc())
        logging.info(f"Error processing column_string: {column_string}")
        raise e
        
# end of extract_kv_tuples function


def extract_dicts_1(column_string, movie_id):
    pass
    
#     # Ensure column_string is a string
#     if not isinstance(column_string, str):
#         return []

#     # Skip empty list values
#     if column_string.strip() == '[]':
#         return []
    
#     # remove the wrapping square brackets
#     clean_column = column_string.strip().strip("[]")
    
#     # split entire value string into curly braced sections
    
#     # within each section find two key-value pairs within 
#     # with key's "id" and "name"
    
#     # ensure keys are wrapped with double quotes
    
#     # ensure that colon comes after each key
    
#     # ensure that value comes after each color
    
#     # replace excaped unicodes in the alue with actual unicode characters

#     # ensure that the value is wrapped with double quotes
#     # but ensure that internal quotes are not chnaged
    
#     # add a final key-value pair with key "movie_id" and value as 
#     # the movie_id passed to the function for the entire column
#     # string.
    
#     # Ensure all keys and values are bounded with double quotes
#     # in each section
    
#     # attempt JSON.parse on each section individually to 
#     # create a python dict object
    
#     # report any sections that are fail JSON parsing
    
#     # add "movie_id" with its value as the third 
#     # key-value pair of the dict object
    
#     # return a list of all dict objects

#     # Ensure all values are bounded with double quotes
#     clean_column = re.sub(r'(?<!")\b([a-zA-Z0-9_]+)\b(?!")', r'"\1"', clean_column)
    
#     # Add movie_id as the third key-value pair
#     clean_column = re.sub(r'({[^}]*})', r'\1, "movie_id": "' + movie_id + '"', clean_column)
    
#     # Parse the dictionary string
#     try:
#         dict_list = json.loads(f"[{clean_column}]")
#     except (ValueError, SyntaxError) as e:
#         logging.error(f"Error parsing dictionary string: {column_string}, error: {e}")
#         raise e

#     return dict_list
    

def table_exists(cursor, table_name):
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = %s
            AND table_name = %s
        )
    """, (DB_SCHEMA, table_name))
    return cursor.fetchone()[0]

def create_fresh_movies_table(conn):
    try:
        cur = conn.cursor()
        logging.info("Dropping and creating the movies table 'movies'.")
        
            # Read the CSV file to get the column names
        with open(MOVIES_CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            column_names = reader.fieldnames
            
            if len(column_names) != MOVIES_CSV_NUM_COLUMNS:
                raise Exception(f"Wrong # column_names: {len(column_names)} found in CSV file.")
            
            if table_exists(cur, 'movies'):
                cur.execute("""
                    DROP TABLE IF EXISTS movies CASCADE
                """)
                conn.commit()
                logging.info("Existing 'movies' table dropped cascade successfully.")
            else:
                logging.info("No existing 'movies' table found.")

            # Create empty table with dynamic columns
            create_table_query = """
                CREATE TABLE IF NOT EXISTS movies (
                    adult TEXT,
                    belongs_to_collection TEXT,
                    budget TEXT,
                    genres TEXT,
                    homepage TEXT,
                    id TEXT,
                    imdb_id TEXT,
                    original_language TEXT,
                    original_title TEXT,
                    overview TEXT,
                    popularity TEXT,
                    poster_path TEXT,
                    production_companies TEXT,
                    production_countries TEXT,
                    release_date TEXT,
                    revenue TEXT,
                    runtime TEXT,
                    spoken_languages TEXT,
                    status TEXT,
                    tagline TEXT,
                    title TEXT,
                    video TEXT,
                    vote_average TEXT,
                    vote_count TEXT
            );
            """
            cur.execute(create_table_query)
            conn.commit()
            logging.info("Empty 'movies' table created successfully.")
            
            # Add PRIMARY KEY constraint to movies table
            cur.execute(sql.SQL("""
                ALTER TABLE movies
                ADD PRIMARY KEY (id)
            """))
            conn.commit()
            logging.info("PRIMARY KEY constraint added to 'movies' table successfully.")
            
    except Exception as e:
        logging.error(f"Error creating 'movies' table: {e}")
        logging.error(traceback.format_exc())
        conn.rollback()
    finally:
        cur.close()

def insert_movies_data_from_csv(conn, csv_file_path, chunk_size=10000):
    total_rows_inserted = 0
    try:
        cur = conn.cursor()
        logging.info(f"Inserting movies data from csv_file_path: {csv_file_path}")
        with open(csv_file_path, 'r') as f:
            dict_reader = csv.DictReader(f)
            column_names = dict_reader.fieldnames
            if len(dict_reader.fieldnames) != MOVIES_CSV_NUM_COLUMNS:
                raise Exception(f"Column_names length mismatch: {len(column_names)} != {MOVIES_CSV_NUM_COLUMNS} in CSV file.")
            rows = []
            for idx, row in enumerate(dict_reader):
                if len(row) != MOVIES_CSV_NUM_COLUMNS:
                    print(f"Skipping row {idx}. Row length: {len(row)} != {MOVIES_CSV_NUM_COLUMNS}")
                    continue
                rows.append(row)
                if len(rows) >= chunk_size:
                    rows_inserted = insert_movies_chunk(cur, rows, column_names)
                    total_rows_inserted += rows_inserted
                    logging.info(f"movies_table row inserts: {total_rows_inserted}")
                    rows = []
            if rows:
                rows_inserted = insert_movies_chunk(cur, rows, column_names)
                total_rows_inserted += rows_inserted
                logging.info(f"movies_table row inserts: {total_rows_inserted}")
        conn.commit()
    except Exception as e:
        logging.error(f"Error inserting data from CSV file: {e}")
        logging.error(traceback.format_exc())
        conn.rollback()
    finally:
        cur.close()
    return total_rows_inserted

def insert_movies_chunk(cursor, rows, column_names):
    try:
        insert_query = sql.SQL("""
            INSERT INTO movies ({columns})
            VALUES ({values})
            ON CONFLICT (id) DO NOTHING
        """).format(
            columns=sql.SQL(', ').join(map(sql.Identifier, column_names)),
            values=sql.SQL(', ').join(sql.Placeholder(name) for name in column_names)
        )
        cursor.executemany(insert_query, rows)
        cursor.connection.commit()
        return len(rows)
    except Exception as e:
        logging.error(f"Error inserting chunk into movies table: {e}")
        logging.error(traceback.format_exc())
        cursor.connection.rollback()
        return 0

def get_columns(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        dict_reader = csv.DictReader(f)
        return dict_reader.fieldnames




# Assuming you have a connection setup
if __name__ == "__main__":
    logging.info("Starting the load_movies.py script...")
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        logging.info("Database connection established successfully.")
        
        # Initialize the schema search path
        cur = conn.cursor()
        cur.execute(sql.SQL("SET search_path TO {schema}").format(schema=sql.Identifier(DB_SCHEMA)))
        conn.commit()
        cur.close()
            
        # Create the movies table
        create_fresh_movies_table(conn)

        # Insert data from CSV file into the movies table
        total_movies_rows = insert_movies_data_from_csv(conn, MOVIES_CSV_PATH)
        logging.info(f"'movies' table rows: {total_movies_rows}")

        # Commented out the creation of column tables
        # total_production_companies_rows = create_fresh_column_table(conn, 'production_companies', 'production_companies', 'production_company')
        # logging.info(f"Total rows inserted into 'production_companies' table: {total_production_companies_rows}")

        # total_genres_rows = create_fresh_column_table(conn, 'genres', 'genres', 'genre')
        # logging.info(f"Total rows inserted into 'genres' table: {total_genres_rows}")

        # total_spoken_languages_rows = create_fresh_column_table(conn, 'spoken_languages', 'spoken_languages', 'spoken_language')
        # logging.info(f"Total rows inserted into 'spoken_languages' table: {total_spoken_languages_rows}")

    except Exception as e:
        logging.error(f"Error establishing database connection: {e}")
        logging.error(traceback.format_exc())
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")