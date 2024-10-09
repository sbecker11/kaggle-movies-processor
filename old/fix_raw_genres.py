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

# read the raw_movies table into memory
# for each row, split the genres column into a json-valid list of dictionaries
# for each dictionary, extract the 'name' key and append it to a list
# join the list into a comma-separated string and update the row
# update the row in the raw_movies table
def fix_raw_genres(cur):
    try:
        cur.execute("SET search_path TO kaggle_schema, public;")
        print("Search path set to kaggle_schema, public before import")
        
        cur.execute("SELECT * FROM kaggle_schema.raw_movies")
        rows = cur.fetchall()
        print(f"Number of rows in raw_movies table: {len(rows)}")
        
        for i, row in enumerate(rows):
            if i < 5:  # Print first 5 rows for debugging
                print(f"Raw row {i+1}: {row}")
                #  [{'iso_639_1': 'ta', 'name': 'தமிழ்'}]
            # genres is in column 3
            genres = row[3]
            if genres:
                genres_list = genres.split(',')
                cleaned_genres = []
                for genre in genres_list:
                    cleaned_genre = genre.replace("'", '"')
                    cleaned_genres.append(cleaned_genre)
                cleaned_genres_str = ','.join(cleaned_genres)
                cur.execute("""
                    UPDATE kaggle_schema.raw_movies
                    SET genres = %s
                    WHERE id = %s
                """, (cleaned_genres_str, row[5]))
                if i < 5:  # Print first 5 cleaned rows for debugging
                    print(f"Cleaned row {i+1}: {row}")
                if i % 1000 == 0:
                    print(f"Processed {i} rows")
                    cur.connection.commit()  # Commit every 1000 rows

        print("Data import attempt completed.")
    except Exception as e:
        print(f"Error importing data: {e}")
        raise

def import_data(cur):
    try:
        cur.execute("SET search_path TO kaggle_schema, public;")
        print("Search path set to kaggle_schema, public before import")
        
        create_table_if_not_exists(cur)

        # Check if the table is empty
        cur.execute("SELECT COUNT(*) FROM kaggle_schema.raw_movies")
        count = cur.fetchone()[0]
        print(f"Current row count in raw_movies table: {count}")

        with open('/Users/sbecker11/workspace-patient-iq/kaggle-movies-processor/movies_metadata.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)  # Skip the header row
            print(f"CSV Headers: {headers}")
            print(f"Number of columns in CSV: {len(headers)}")
            
            insert_query = sql.SQL("""
                INSERT INTO kaggle_schema.raw_movies (
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
        cur.execute("SELECT COUNT(*) FROM kaggle_schema.raw_movies")
        final_count = cur.fetchone()[0]
        print(f"Final row count in raw_movies table: {final_count}")
    except Exception as e:
        print(f"Error importing data: {e}")
        raise

def main():
    user = 'db_admin'
    pswd = os.getenv('DB_ADMIN_PASSWORD')
    if not pswd:
        raise ValueError("DB_ADMIN_PASSWORD not set in .env file")

    conn = psycopg2.connect(
        dbname="database",
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