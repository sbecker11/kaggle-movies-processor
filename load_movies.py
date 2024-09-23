import csv
import re
import psycopg2
from psycopg2 import sql
import logging
import os
import traceback
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

POSTGRES_USER = os.getenv('DB_USER')
POSTGRES_PASSWORD = os.getenv('DB_PASSWORD')
POSTGRES_HOST = os.getenv('DB_HOST', 'localhost')
POSTGRES_PORT = os.getenv('DB_PORT', '5432')
POSTGRES_DB = os.getenv('DB_NAME', 'patient_iq')
SCHEMA = os.getenv('DB_SCHEMA', 'patient_iq_schema')
MOVIES_TABLE="movies"
NUM_MOVIES_COLUMNS = 24
MOVIES_CSV_PATH = '/Users/sbecker11/workspace-patient-iq/kaggle-movies-processor/movies_metadata.csv'

def drop_table_if_exists(conn, table_name):
    """Drop the table if it exists in the SCHEMA."""
    with conn.cursor() as cur:
        cur.execute(f"DROP TABLE IF EXISTS {SCHEMA}.{table_name} CASCADE")
        conn.commit()
    print(f"Table {table_name} dropped if it existed.")

def count_rows_in_table(cur, table_name):
    """Return the number of rows in the table in the SCHEMA."""
    count_query = sql.SQL("""
    SELECT COUNT(*) FROM {schema}.{table}
    """).format(
        schema=sql.Identifier(SCHEMA),
        table=sql.Identifier(table_name)
    )
    cur.execute(count_query)
    result = cur.fetchone()[0]
    return result

def get_column_names(conn, schema, table_name):
    with conn.cursor() as cur:
        # Query to get column names
        query = sql.SQL("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
        """)
        
        # Execute the query
        cur.execute(query, (schema, table_name))
        
        # Fetch all results
        columns = cur.fetchall()
        
        # Extract column names from the results
        column_names = [col[0] for col in columns]
        
        return column_names

def bbq(item):
    if type(item) == str:
        return item.strip().strip('"').strip("'")
    else:
        return item

def split_dict_str(dict_str):
    # split the dict string into two key/value pairs
    # for example, given dict_str: "'name': 'Jim Henson Company, The', 'id': 6254"
    # should return 2 key_value_pairs: 
    # ['name','Jim Henson Company, The'] and ['id',6254"]
    key_value_pairs = []
    kv_pairs = re.findall(r"'(.*?)':\s?'(.*?)'", dict_str)
    for kv_pair in kv_pairs:
        key = kv_pair[0]
        value = kv_pair[1]
        key_value_pairs.append([key,value])
    return key_value_pairs

def get_key_value_pairs(clean_column):
    # given a clean_column '"name"': "'Pixar Animation Studios'"", 'id': 3"
    # return key_value_pairs: [('name','Pixar Animation Studios'), ('id',3)]
    # Regular expression to match key-value pairs
    pattern = re.compile(r"'(.*?)':\s?'(.*?)'|'(.*?)':\s?(\d+)")
    
    # Find all matches in the clean_column
    matches = pattern.findall(clean_column)
    
    key_value_pairs = []
    for match in matches:
        if match[0] and match[1]:  # If both key and value are quoted strings
            key_value_pairs.append((match[0], match[1]))
        elif match[2] and match[3]:  # If key is a quoted string 
            key_value_pairs.append((match[2], match[3]))
    
    return key_value_pairs

def test_parse_row_dicts_from_from_column():
    # Sample input data
    sample_data = [
        {"id": 1, "column_data": ["{'key1': 'value1', 'key2': 'value2'}"]},
        {"id": 2, "column_data": ["{'key3': 'value3', 'key4': 'value4'}"]}
    ]
    
    # Expected output
    expected_output = [
        {"id": 1, "key1": "value1", "key2": "value2"},
        {"id": 2, "key3": "value3", "key4": "value4"}
    ]
    
    # Call the function
    output = parse_row_dicts_from_from_column(sample_data, "column_data")
    
    # Check if the output matches the expected output
    assert output == expected_output, f"Expected {expected_output}, but got {output}"
    
    print("test_parse_row_dicts_from_from_column passed")



# given a dict_str/row_column, parse the name and id properties
#  a row_column "[{'name': 'Pixar Animation Studios', 'id': 3}]"
# return an array of a single dict object with the name, id, 
# and movie_id properties
# { 'name':  'Pixar Animation Studios', 'id':3, movie_id: 862 }
# otherwise return an empty array
def parse_row_dicts_from_from_column(row_column, movie_id):
    clean_column = row_column.strip().strip("[]").strip("{}")
    key_value_pairs = get_key_value_pairs(clean_column)
    if not key_value_pairs:
        logging.error(f"Error parsing row_column: {row_column}")
        return []
    name = id = None
    for key_value_pair in key_value_pairs:
        key = bbq(key_value_pair[0])
        value = bbq(key_value_pair[1])
        if key == 'name':
            name = value
        elif key == 'id':
            id = value
        else:
            logging.error(f"Unknown key: {key} in row_column: {row_column}")
            return []
    if name and id:
        cleaned_dict = {
            'movie_id': movie_id,
            'id': id,
            'name': name
        }
        return [cleaned_dict]
    else:
        logging.error(f"Error parsing row_column: {row_column}")
        return []


def create_movies_table(conn):
    """Create the MOVIES_TABLE in the SCHEMA."""
    logging.info(f"creating {MOVIES_TABLE} table in {SCHEMA}.")
    with conn.cursor() as cur:
        cur.execute(sql.SQL("""
        CREATE TABLE {schema}.{movies} (
            adult TEXT,
            belongs_to_collection TEXT,
            budget TEXT,
            genres TEXT,
            homepage TEXT,
            id TEXT PRIMARY KEY,
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
        )
        """).format(
            schema=sql.Identifier(SCHEMA),
            movies=sql.Identifier(MOVIES_TABLE)
        )
    )
    conn.commit()
    print("movies table created.")

def create_fresh_movies_table(conn):
    """Drop, create, and load movies table from CSV file."""
    try:
        with conn.cursor() as cur:
            # Drop and recreate the movies table
            drop_table_if_exists(conn, MOVIES_TABLE)
            create_movies_table(conn)

            # Check if the CSV file exists
            if not os.path.exists(MOVIES_CSV_PATH):
                raise FileNotFoundError(f"File not found: {MOVIES_CSV_PATH}")

            # Load data from CSV file
            with open(MOVIES_CSV_PATH, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)  # Skip the header row
                print(f"CSV Headers: {headers}")
                num_columns = len(headers)
                if num_columns != NUM_MOVIES_COLUMNS:
                    raise ValueError(f"Expected {NUM_MOVIES_COLUMNS} columns, but got {num_columns} columns")
                
                logging.info(f"Loading data from {MOVIES_CSV_PATH} into {MOVIES_TABLE} table in {SCHEMA}.")
                
                insert_query = sql.SQL("""
                    INSERT INTO {schema}.{movies} (
                        adult, belongs_to_collection, budget, genres, homepage, id, imdb_id,
                        original_language, original_title, overview, popularity, poster_path,
                        production_companies, production_countries, release_date, revenue,
                        runtime, spoken_languages, status, tagline, title, video,
                        vote_average, vote_count
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (id) DO NOTHING
                """).format(
                    schema=sql.Identifier(SCHEMA),
                    movies=sql.Identifier(MOVIES_TABLE)
                )
                num_rows_saved = 0
                for i, row in enumerate(reader):
                    if len(row) != NUM_MOVIES_COLUMNS:
                        logging.error(f"Row {i+1} has {len(row)} columns, but expected {NUM_MOVIES_COLUMNS} columns.")

                    if i < 5:  # Print first 5 rows for debugging
                        print(f"Raw CSV row {i+1}: {row}")
                    cleaned_fields = [field.strip() for field in row]
                    if i < 5:  # Print first 5 cleaned rows for debugging
                        print(f"Cleaned fields {i+1}: {cleaned_fields}")
                    if len(cleaned_fields) != NUM_MOVIES_COLUMNS:
                        logging.error(f"Row {i+1} has {len(cleaned_fields)} cleaned fields, but expected {NUM_MOVIES_COLUMNS} cleaned fields.")
                        logging.error(f"Row {i+1} skipped")
                        continue
                    cur.execute(insert_query, cleaned_fields)
                    num_rows_saved += 1
                    if i % 1000 == 0:
                        print(f"Processed {i} rows")
                        conn.commit()  # Commit every 1000 rows
                conn.commit()  # Commit any remaining rows
                
            print(f"{MOVIES_TABLE} table saved {num_rows_saved} out of {i} rows.")
            
            # Check final row count
            final_count = count_rows_in_table(cur, MOVIES_TABLE)    
            print(f"Final row count in {MOVIES_TABLE} table: {final_count}")
    except Exception as e:
        logging.error("loading movies data: {e}")
        logging.error(traceback.format_exc()) 
        conn.rollback()
        conn.close()
        raise

def create_column_table_if_not_exists(conn, table_name, column_name, column_name_singular):
    try:
        cur = conn.cursor()
        cur.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {schema}.{table_name} (
                movie_id TEXT,
                {id_key} TEXT,
                {name_key} TEXT
            )
        """).format(
            schema=sql.Identifier(SCHEMA),
            table_name=sql.Identifier(table_name),
            id_key=sql.Identifier(column_name_singular + '_id'),
            name_key=sql.Identifier(column_name_singular + '_name')
        ))
        conn.commit()
        print(f"Table {table_name} created successfully.")
    except Exception as e:
        logging.error(f"Error creating table {table_name}: {e}")
        logging.error(traceback.format_exc())
        conn.rollback()
    finally:
        cur.close()

def insert_column_table_in_chunks(cursor, data, table_name, column_name_singular, chunk_size=1000):
    insert_query = sql.SQL("""
        INSERT INTO {schema}.{table_name} ({movie_id}, {id_key}, {name_key})
        VALUES (%s, %s, %s)
    """).format(
        schema=sql.Identifier(SCHEMA),
        table_name=sql.Identifier(table_name),
        movie_id=sql.Identifier('movie_id'),
        id_key=sql.Identifier(column_name_singular + '_id'),
        name_key=sql.Identifier(column_name_singular + '_name')
    )
    
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        try:
            cursor.executemany(insert_query, chunk)
            cursor.connection.commit()
        except Exception as e:
            cursor.connection.rollback()
            print(f"Error inserting chunk: {e}")

def create_fresh_column_table(conn, table_name, column_name, column_name_singular):
    try:
        cur = conn.cursor()
        
        # Drop the table if it exists
        cur.execute(sql.SQL("DROP TABLE IF EXISTS {schema}.{table_name}").format(
            schema=sql.Identifier(SCHEMA),
            table_name=sql.Identifier(table_name)
        ))
        conn.commit()
        print(f"Table {table_name} dropped successfully.")
        
        # Create the table
        create_column_table_if_not_exists(conn, table_name, column_name, column_name_singular)
        
        # Fetch the data to insert
        cur.execute(sql.SQL("""
            SELECT
                id AS movie_id,
                unnest((regexp_matches({column_name}::text, E'\\{[^\\}]+\\}', 'g'))::text[]) AS {id_key},
                unnest((regexp_matches({column_name}::text, E'\\{[^\\}]+\\}', 'g'))::text[]) AS {name_key}
            FROM
                movies
        """).format(
            column_name=sql.Identifier(column_name),
            id_key=sql.Identifier(column_name_singular + '_id'),
            name_key=sql.Identifier(column_name_singular + '_name')
        ))
        column_data = cur.fetchall()
        
        # Insert data in chunks
        insert_column_table_in_chunks(cur, column_data, table_name, column_name_singular, chunk_size=1000)
        
    except Exception as e:
        logging.error(f"Error processing {table_name} data: {e}")
        logging.error(traceback.format_exc())
        conn.rollback()
    finally:
        cur.close()
    

if __name__ == "__main__":
    
    logging.basicConfig(level=logging.INFO)
    
    conn = psycopg2.connect(
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT
    )
    try:
        with conn.cursor() as cur:
            cur.execute(f"SET search_path TO {SCHEMA}, public;")
            logging.info(f"Schema search_path set to {SCHEMA}, public.")
            conn.commit()
            
        test_parse_row_dicts_from_from_column()
        
        # Drop, create, and load the movies table
        # create_fresh_movies_table(conn)
        
        # Create fresh production_companies table
        # create_fresh_column_table(conn, 'production_companies', 'production_companies', 'production_company')

        # Create fresh genres table
        # create_fresh_column_table(conn, 'genres', 'genres', 'genre')

        # Create fresh spoken_languages table
        # create_fresh_column_table(conn, 'spoken_languages', 'spoken_languages', 'spoken_language')


    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.error(traceback.format_exc())
        conn.rollback()
        logging.error(f"An error occurred: {e}")
        logging.error(traceback.format_exc())
    finally:
        conn.close()
        logging.info("Connection closed.")
        logging.shutdown()
        print("Done.")