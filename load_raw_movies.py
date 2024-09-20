import csv
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import logging
import os

# Generate a movies table along with three other tables 
# (genres, production_companies, and languages).  
# You will be using these tables in the next section for querying.

load_dotenv()

POSTGRES_USER = 'db_admin'
POSTGRES_PASSWORD = os.getenv('DB_ADMIN_PASSWORD')
POSTGRES_HOST = 'localhost'
POSTGRES_PORT = '5432'
POSTGRES_DB = 'patient_iq'
CURRENT_SCHEMA = 'patient_iq_schema'

META_MOVIES_CSV_PATH = '/Users/sbecker11/workspace-patient-iq/kaggle-movies-processor/movies_metadata.csv'


def clean_and_pad_row(row):
    """Ensure the row has at least 24 elements by padding with empty strings."""
    while len(row) < 24:
        row.append('')
    return row

def table_exists(cur, table_name):
    """Check if a table exists in the CURRENT_SCHEMA."""
    cur.execute("""
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables 
        WHERE table_schema = %s
        AND table_name = %s
    )
    """, (CURRENT_SCHEMA, table_name))
    return cur.fetchone()[0]


def count_rows_in_table(cur, table_name):
    """return the number of rows in the table in the CURRENT_SCHEMA"""
    cur.execute(f"SELECT COUNT(*) FROM {CURRENT_SCHEMA}.{table_name}")
    return cur.fetchone()[0]

def truncate_raw_movies_table_if_exists(cur):
    """truncate raw_movies table in the CURRENT_SCHEMA if it exists"""
    
    if not table_exists(cur, 'raw_movies'):
        print("raw_movies table does not exist, skipping truncation.")
        return
    
    count = count_rows_in_table(cur, 'raw_movies')
    print(f"Current row count in raw_movies table: {count}")
    if count > 0:
        cur.execute(f"TRUNCATE TABLE {CURRENT_SCHEMA}.raw_movies")
        print("raw_movies_table truncated.")
    else:
        print("raw_movies_table is already empty.")

def create_raw_movies_table_if_not_exists(cur):
    """create raw_movies table in the CURRENT_SCHEMA if it does not exist"""
    
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS {CURRENT_SCHEMA}.raw_movies (
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
    )
    """)
    print("raw_movies_table created.")

def fresh_load_raw_movies_table(cur):
    """truncate and load raw_movies table from csv file"""
    try:
        # search path first to CURRENT_SCHEMA and if not found then public
        cur.execute(f"SET search_path TO {CURRENT_SCHEMA}, public;")
        print(f"Search path set to {CURRENT_SCHEMA}, public before import")
        
        # Trancate and create empty raw_movies table
        truncate_raw_movies_table_if_exists(cur)
        
        create_raw_movies_table_if_not_exists(cur)

        # verify that table exists and is empty
        count = count_rows_in_table(cur, 'raw_movies')
        if count == 0:
            print("raw_movies table is empty.")
        else:
            raise Exception("raw_movies table is not empty.")
        
        # check to see if movies csv file exists
        if not os.path.exists(META_MOVIES_CSV_PATH):
            raise FileNotFoundError(f"File not found: {META_MOVIES_CSV_PATH}")

        # attempt to load data from csv file
        with open(META_MOVIES_CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)  # Skip the header row
            print(f"CSV Headers: {headers}")
            print(f"Number of columns in CSV: {len(headers)}")
            
            insert_query = sql.SQL(f"""
                INSERT INTO {CURRENT_SCHEMA}.raw_movies (
                    adult, belongs_to_collection, budget, genres, homepage, id, imdb_id,
                    original_language, original_title, overview, popularity, poster_path,
                    production_companies, production_countries, release_date, revenue,
                    runtime, spoken_languages, status, tagline, title, video,
                    vote_average, vote_count
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
            """)
            
            for i, row in enumerate(reader):
                if i < 5:  # Print first 5 rows for debugging
                    print(f"Raw CSV row {i+1}: {row}")
                cleaned_row = clean_and_pad_row(row)
                if i < 5:  # Print first 5 cleaned rows for debugging
                    print(f"Cleaned row {i+1}: {cleaned_row}")
                cur.execute(insert_query, cleaned_row)
                if i % 1000 == 0:
                    print(f"Processed {i} rows")
                    cur.connection.commit()  # Commit every 1000 rows

        print("attempted raw_movies table load completed.")
        
        # Check final row count
        final_count = count_rows_in_table(cur, 'raw_movies')    
        print(f"Final row count in raw_movies table: {final_count}")
    except Exception as e:
        print(f"Error loading raw_movies data: {e}")
        raise



def fresh_create_filtered_table_and_sequence(cur, table_name, column_name):
    try:
        # Check if the table exists before truncating
        if table_exists(cur, table_name):
            cur.execute(f"TRUNCATE TABLE {CURRENT_SCHEMA}.{table_name} RESTART IDENTITY CASCADE")
            logging.info(f"{table_name} table truncated and sequence restarted.")
        else:
            logging.info(f"{table_name} table does not exist, skipping truncation.")
        
        # Create the table if it does not exist
        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {CURRENT_SCHEMA}.{table_name} (
            id SERIAL PRIMARY KEY,
            {column_name} TEXT
        )
        """)
        logging.info(f"{table_name} table and sequence created if needed.")
        
        # Check if the table was created
        if not table_exists(cur, table_name):
            logging.info(f"{table_name} table was created.")
        else:
            logging.info(f"{table_name} table already existed.")
    except Exception as e:
        logging.error(f"Error creating {table_name} table: {e}")
        raise

def refresh_genres_table(cur):
    fresh_create_filtered_table_and_sequence(cur, 'genres', 'genre')
    logging.info("genres table refreshed.")

def refresh_production_companies_table(cur):
    fresh_create_filtered_table_and_sequence(cur, 'production_companies', 'production_companies')
    logging.info("production_companies table refreshed.")

def refresh_spoken_languages_table(cur):
    fresh_create_filtered_table_and_sequence(cur, 'spoken_languages', 'spoken_languages')
    logging.info("spoken_languages table refreshed.")

def main():
    user = POSTGRES_USER
    pswd = POSTGRES_PASSWORD
    if not pswd:
        raise ValueError("DB_ADMIN_PASSWORD not set in .env file")

    conn = psycopg2.connect(
        dbname="patient_iq",
        user=user,
        password=pswd,
        host="localhost"
    )
    cur = conn.cursor()

    try:
        # Check current user and search path
        cur.execute("SELECT current_user, current_schema;")
        current_user, current_schema = cur.fetchone()
        print(f"Connected as user: {current_user}, current schema: {current_schema}")

        fresh_load_raw_movies_table(cur)
        conn.commit()
        print("load_raw_movies_table committed.")
        
        refresh_genres_table(cur)
        conn.commit()

        refresh_production_companies_table(cur)
        conn.commit()

        refresh_spoken_languages_table(cur)
        conn.commit()

        print("refresh filtered tables completed successfully.")
    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()