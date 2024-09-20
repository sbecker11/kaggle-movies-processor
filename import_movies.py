import csv
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

load_dotenv()

def clean_and_pad_row(row):
    while len(row) < 24:
        row.append('')
    return row

def create_table_if_not_exists(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS patient_iq_schema.movies (
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
    print("Table creation check completed.")

def import_data(cur):
    try:
        cur.execute("SET search_path TO patient_iq_schema, public;")
        print("Search path set to patient_iq_schema, public before import")
        
        create_table_if_not_exists(cur)

        # Check if the table is empty
        cur.execute("SELECT COUNT(*) FROM patient_iq_schema.movies")
        count = cur.fetchone()[0]
        print(f"Current row count in movies table: {count}")

        with open('/Users/sbecker11/workspace-patient-iq/kaggle-movies-processor/movies_metadata.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)  # Skip the header row
            print(f"CSV Headers: {headers}")
            print(f"Number of columns in CSV: {len(headers)}")
            
            insert_query = sql.SQL("""
                INSERT INTO patient_iq_schema.movies (
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

        print("Data import attempt completed.")
        
        # Check final row count
        cur.execute("SELECT COUNT(*) FROM patient_iq_schema.movies")
        final_count = cur.fetchone()[0]
        print(f"Final row count in movies table: {final_count}")
    except Exception as e:
        print(f"Error importing data: {e}")
        raise

def main():
    superuser_name = 'sbecker11'
    superuser_password = os.getenv('SUPERUSER_PASSWORD')
    if not superuser_password:
        raise ValueError("SUPERUSER_PASSWORD not set in .env file")

    conn = psycopg2.connect(
        dbname="patient_iq",
        user=superuser_name,
        password=superuser_password,
        host="localhost"
    )
    cur = conn.cursor()

    try:
        # Check current user and search path
        cur.execute("SELECT current_user, current_schema;")
        current_user, current_schema = cur.fetchone()
        print(f"Connected as user: {current_user}, current schema: {current_schema}")

        import_data(cur)
        conn.commit()
        print("Data import committed.")
        
        print("All operations completed successfully.")
    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()