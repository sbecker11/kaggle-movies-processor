import csv
import json
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

def clean_and_pad_row(row):
    """
    Clean and pad a row from the CSV file to match the expected schema.
    This function ensures that the row has the correct number of columns
    and cleans any necessary data.
    """
    # Define the expected number of columns
    expected_columns = 24
    
    # Clean the row data
    cleaned_row = [col.strip() if col else None for col in row]
    
    # Pad the row with None values if it has fewer columns than expected
    if len(cleaned_row) < expected_columns:
        cleaned_row.extend([None] * (expected_columns - len(cleaned_row)))
    
    # Truncate the row if it has more columns than expected
    if len(cleaned_row) > expected_columns:
        cleaned_row = cleaned_row[:expected_columns]
    
    return cleaned_row

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
                print(f"Number of columns in CSV: {len(headers)}")
                
                logging.info(f"Loading data from {MOVIES_CSV_PATH} into {MOVIES_TABLE} table in {SCHEMA}.")
                
                insert_query = sql.SQL("""
                    INSERT INTO {schema}.{movies} (
                        adult, belongs_to_collection, budget, genres, homepage, id, imdb_id,
                        original_language, original_title, overview, popularity, poster_path,
                        production_companies, production_countries, release_date, revenue,
                        runtime, spoken_languages, status, tagline, title, video,
                        vote_average, vote_count
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (id) DO NOTHING
                """).format(
                    schema=sql.Identifier(SCHEMA),
                    movies=sql.Identifier(MOVIES_TABLE)
                )
                for i, row in enumerate(reader):
                    if i < 5:  # Print first 5 rows for debugging
                        print(f"Raw CSV row {i+1}: {row}")
                    cleaned_row = clean_and_pad_row(row)
                    if i < 5:  # Print first 5 cleaned rows for debugging
                        print(f"Cleaned row {i+1}: {cleaned_row}")
                    cur.execute(insert_query, cleaned_row)
                    if i % 1000 == 0:
                        print(f"Processed {i} rows")
                        conn.commit()  # Commit every 1000 rows
                conn.commit()  # Commit any remaining rows
            print(f"Attempted {MOVIES_TABLE} table load completed.")
            
            # Check final row count
            final_count = count_rows_in_table(cur, MOVIES_TABLE)    
            print(f"Final row count in {MOVIES_TABLE} table: {final_count}")
    except Exception as e:
        logging.error("loading movies data: {e}")
        logging.error(traceback.format_exc()) 
        conn.rollback()
        conn.close()
        raise

def create_fresh_column_table(conn, table_name, column_name, singular_column_name):
    try:
        drop_table_if_exists(conn, table_name)
        logging.info(f"{table_name} table dropped if it existed.")

        with conn.cursor() as cur:
            
            # Replace \x9a characters with 'š' in the movies_table column
            cur.execute(sql.SQL("""
                UPDATE {schema}.{movies_table}
                SET {column_name} = REPLACE({column_name}, '\x9a', 'š')
                WHERE {column_name} LIKE '%\\x%' and {column_name} is not null
                """).format(
                    schema=sql.Identifier(SCHEMA),
                    movies_table=sql.Identifier(MOVIES_TABLE),
                    column_name=sql.Identifier(column_name)
                )
            )
            conn.commit()
            logging.info(f"Escape characters replaced in {column_name} column of {MOVIES_TABLE} table")
            
            # Replace single quotes with double quotes
            cur.execute(sql.SQL("""
                UPDATE {schema}.{movies_table}
                SET {column_name} = 
                REGEXP_REPLACE({column_name},  E'^\\s*\'', '"' ) -- replace leading single 
                WHERE {column_name} is not null
                """).format(
                    schema=sql.Identifier(SCHEMA),
                    movies_table=sql.Identifier(MOVIES_TABLE),
                    column_name=sql.Identifier(column_name)
                )
            )
            conn.commit()
            logging.info(f"Replaced leading single quotes in {column_name} column of {MOVIES_TABLE} table")

            cur.execute(sql.SQL("""
                UPDATE {schema}.{movies_table}
                SET {column_name} = 
                REGEXP_REPLACE({column_name}, E'\'\\s*$', '"')
                WHERE {column_name} is not null
                """).format(
                    schema=sql.Identifier(SCHEMA),
                    movies_table=sql.Identifier(MOVIES_TABLE),
                    column_name=sql.Identifier(column_name)
                )
            )
            conn.commit()
            logging.info(f"Replaced trailing single quotes in {column_name} column of {MOVIES_TABLE} table")
        
            # cast column_name column to jsonb
            cur.execute(sql.SQL("""
                UPDATE {schema}.{movies_table}
                SET {column_name} = {column_name}::jsonb
                WHERE {column_name} is not null
                """).format(
                    schema=sql.Identifier(SCHEMA),
                    movies_table=sql.Identifier(MOVIES_TABLE),
                    column_name=sql.Identifier(column_name)
                )
            )
            conn.commit()
            logging.info(f"{column_name} column cast to jsonb in {MOVIES_TABLE} table.")
            
            # create column table
            cur.execute(sql.SQL("""
                CREATE TABLE  IF NOT EXISTS {schema}.{table_name} (
                    movie_id TEXT,
                    {singular_column_name}_id TEXT,
                    {singular_column_name}_name TEXT
                );
                """).format(
                    schema=sql.Identifier(SCHEMA),
                    table_name=sql.Identifier(table_name),
                    singular_column_name=sql.Identifier(singular_column_name),
                        column_table=sql.Identifier(table_name)
                )
            )      
            logging.info(f"{table_name} table created with new movie_id and {singular_column_name} columns for jsonb dict properties.")
            conn.commit()              
            
            # explode json arrays of dict in column into separate rows
            # with movie_id and singular_column_name columns
            cur.execute(sql.SQL("""
                INSERT INTO {schema}.{table_name} (movie_id, {singular_column_name}_id, {singular_column_name}_name)
                SELECT 
                    m.id AS movie_id,
                    {column_name}->>'id' AS {singular_column_name}_id,
                    {column_name}->>'name' AS {singular_column_name}_name
                FROM 
                    {schema}.{movies_table} m,
                    LATERAL jsonb_array_elements_text({column_name}) AS {singular_column_name}
                """).format(
                    schema=sql.Identifier(SCHEMA),
                    column_table=sql.Identifier(table_name),
                    column_name=sql.Identifier(column_name),
                    singular_column_name=sql.Identifier(singular_column_name),
                    movies_table=sql.Identifier(MOVIES_TABLE)
                )
            )
            logging.info(f"{MOVIES_TABLE}.{column_name} column data exploded into new rows with {singular_column_name} columns in {table_name} table.")
        conn.commit()
    except Exception as e:
        logging.error(f"Error processing {column_name} data: {e}")
        logging.error(traceback.format_exc())
        conn.rollback()
        conn.close()


if __name__ == "__main__":
    
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
            
            cur.execute(sql.SQL("""
                UPDATE {schema}.{movies_table}
                SET {column_name} = 
                    REGEXP_REPLACE({column_name}::text, E'\'\\s*$', '"')  -- Replace trailing single quote
                    REGEXP_REPLACE({column_name}::text, E'\'\\s*$', '"')
                WHERE {column_name} IS NOT NULL;
            """).format(
                schema=sql.Identifier(SCHEMA),
                movies_table=sql.Identifier(MOVIES_TABLE),
                column_name=sql.Identifier('production_companies')
            ))
            conn.commit()
            cur.close()
            conn.close()
            logging.info("Single trailing quotes replaced with double quotes in production_companies column.")
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON data: {e}")
        logging.error(traceback.format_exc())
        conn.rollback()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.error(traceback.format_exc())
        conn.rollback()
    finally:
        cur.close()
        
    try:        
        # Set the schema search path
        with conn.cursor() as cur:
            cur.execute(f"SET search_path TO {SCHEMA}, public;")
            logging.info(f"Schema search_path set to {SCHEMA}, public.")
        
        # Drop, create, and load the movies table
        # create_fresh_movies_table(conn)
        
        # Drop, create, and load columns tables
        # create_fresh_column_table(conn,'genres', 'genres', 'genre')
        # create_fresh_column_table(conn,'production_companies', 'production_companies', 'production_company')
        # create_fresh_column_table(conn,'spoken_languages', 'spoken_languages', 'spoken_language')

    except Exception as e:
        conn.rollback()
        logging.error(f"An error occurred: {e}")
        logging.error(traceback.format_exc())
    finally:
        conn.close()