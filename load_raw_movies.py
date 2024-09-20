import csv
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import logging
import os

# Generate a movies table along with three other tables 
# (genres, production_companies, and languages).  
# You will be using these tables in the next section for querying.

META_MOVIES_CSV_PATH = '/Users/sbecker11/workspace-patient-iq/kaggle-movies-processor/movies_metadata.csv'

load_dotenv()

def clean_and_pad_row(row):
    while len(row) < 24:
        row.append('')
    return row

def table_exists(cur, table_name):
    cur.execute("""
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables 
        WHERE table_schema = 'patient_iq_schema' 
        AND table_name = %s
    )
    """, (table_name,))
    return cur.fetchone()[0]


def truncate_raw_movies_table_if_exists(cur):
    cur.execute("SELECT COUNT(*) FROM patient_iq_schema.raw_movies")
    count = cur.fetchone()[0]
    print(f"Current row count in raw_movies table: {count}")
    if count > 0:
        cur.execute("TRUNCATE TABLE patient_iq_schema.raw_movies")
        print("raw_movies_table truncated.")
    else:
        print("raw_movies_table is already empty.")

def create_raw_movies_table_if_not_exists(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS patient_iq_schema.raw_movies (
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
    try:
        cur.execute("SET search_path TO patient_iq_schema, public;")
        print("Search path set to patient_iq_schema, public before import")
        
        # Trancate and create empty raw_movies table
        truncate_raw_movies_table_if_exists(cur)
        
        create_raw_movies_table_if_not_exists(cur)

        # verify that table exists and is empty
        cur.execute("SELECT COUNT(*) FROM patient_iq_schema.raw_movies")
        count = cur.fetchone()[0]
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
            
            insert_query = sql.SQL("""
                INSERT INTO patient_iq_schema.raw_movies (
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
        cur.execute("SELECT COUNT(*) FROM patient_iq_schema.raw_movies")
        final_count = cur.fetchone()[0]
        print(f"Final row count in raw_movies table: {final_count}")
    except Exception as e:
        print(f"Error loading raw_movies data: {e}")
        raise



def refresh_filtered_table_and_sequence(cur, table_name, column_name):
    try:
        # Check if the table exists before creation
        table_existed_before = table_exists(cur, table_name)

        # truncate and create genres table
        cur.execute(f"TRUNCATE TABLE IF EXISTS patient_iq_schema.{table_name} RESTART IDENTITY CASCADE")
        logging.info(f"{table_name} table truncated and sequence restarted.")
        
        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS patient_iq_schema.{table_name} (
            id SERIAL PRIMARY KEY,
            {column_name} TEXT
        )
        """)
        logging.info(f"{table_name} table created from column {column_name} and sequence created if needed.")
        
        table_existed_after = table_exists(cur, table_name)

        if not table_existed_before and table_existed_after:
            logging.info(f"{table_name} table was created.")
        else:
            logging.info(f"{table_name} table already existed.")

    except Exception as e:
        logging.error(f"Error creating {table_name} table from column {column_name}: {e}")
        raise

def refresh_genres_table(cur):
    refresh_filtered_table_and_sequence(cur, 'genres', 'genre')
    logging.info("genres table refreshed.")

def refresh_production_companies_table(cur):
    refresh_filtered_table_and_sequence(cur, 'production_companies', 'production_companies')
    logging.info("production_companies table refreshed.")

def refresh_spoken_languages_table(cur):
    refresh_filtered_table_and_sequence(cur, 'spoken_languages', 'spoken_languages')
    logging.info("spoken_languages table refreshed.")

def main():
    user = 'db_admin'
    pswd = os.getenv('DB_ADMIN_PASSWORD')
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

        print("create filtered tables completed successfully.")
    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()