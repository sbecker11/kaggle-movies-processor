import logging
import csv
from psycopg2 import sql
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

def create_fresh_movies_table(conn, schema, movies_table, rows, columns):
    """Create a fresh table with columns and insert rows into it."""
    try:
        if 'id' not in columns:
            raise Exception("The 'id' column is required to be used as a non-sequential primary key.")
        
        text_columns_without_id = columns.copy() 
        text_columns_without_id.remove('id')
        
        drop_table_if_exists(conn, schema, movies_table)
        logging.info(f"{movies_table} table dropped.")
        if table_exists(conn.cursor(), schema, movies_table):
            raise Exception(f"Table {movies_table} still exists")
                            
        # Use the columns to create the movies table 
        # with a non-sequential primary key id column
        with conn.cursor() as cur:
            create_movies_table_query = sql.SQL("""
            CREATE TABLE {schema}.{table} (
                id TEXT PRIMARY KEY,
                {text_columns_without_id}
            )
            """).format(
                schema=sql.Identifier(schema),
                table=sql.Identifier(movies_table),
                text_columns_without_id=sql.SQL(', ').join(
                    sql.SQL("{} TEXT").format(sql.Identifier(col)) for col in text_columns_without_id
                )
            )
            cur.execute(create_movies_table_query)
            conn.commit()
        logging.info(f"{movies_table} table created.")
        
         # Insert the rows into the movies table
        with conn.cursor() as cur:
            insert_query = sql.SQL("""
            INSERT INTO {schema}.{table} VALUES %s
            """).format(
                schema=sql.Identifier(schema),
                table=sql.Identifier(movies_table)
            )
            psycopg2.extras.execute_values(cur, insert_query, rows)
            conn.commit()
        logging.info(f"{len(rows)} rows inserted into {movies_table} table.")
        
    except Exception as e:
        logging.error(f"Error: {e}")
        conn.rollback()
        logging.info("Transaction rolled back.")
        raise


def create_fresh_column_table(conn, schema, table_name, column_names, movies_table):
    """
    Always create the column table from scratch. If it exists, delete it,
    then always create it from the specified column of the raw_movies table.
    The column table will have a foreign key reference to movies_table.id.
    
    :param conn: Connection object
    :param schema: Schema name
    :param table_name: Name of the table to create
    :param column_names: List of column names to include in the new table
    :param movies_table: Name of the table containing the movies id
    """
    try:
        if not table_exists(conn.cursor(), schema, movies_table):
            raise Exception(f"{movies_table} does not exist")
        
        drop_table_if_exists(conn, schema, table_name)
        if table_exists(conn.cursor(), schema, table_name):
            raise Exception(f"{table_name} table still exists")
        
        if 'movies_id' in column_names:
            raise Exception("The 'movies_id' column is not allowed because it's added automatically.")
        
        # remember to check the column names against the raw_movies table
        with conn.cursor() as cur:
            # Create the new table from the columns of the raw_movies table
            create_table_query = sql.SQL("""
            CREATE TABLE {schema}.{table} AS
            SELECT {columns}, id AS movies_id
            FROM {schema}.raw_movies
            """).format(
                schema=sql.Identifier(schema),
                table=sql.Identifier(table_name),
                columns=sql.SQL(', ').join(sql.Identifier(col) for col in column_names)
            )
            cur.execute(create_table_query)
            
            # Add the foreign key constraint to movies_table.id named fk_table_name_movies
            add_foreign_key_query = sql.SQL("""
            ALTER TABLE {schema}.{table_name}
            ADD CONSTRAINT fk_{table_name}_movies
            FOREIGN KEY (movies_id) REFERENCES {schema}.{movies_table}(id)
            """).format(
                schema=sql.Identifier(schema),
                table_name=sql.Identifier(table_name),
                movies_table=sql.Identifier(movies_table)
            )
            cur.execute(add_foreign_key_query)
            conn.commit()
            
        if not table_exists(conn.cursor(), schema, movies_table):
            raise Exception(f"{movies_table} does not exist")

        drop_table_if_exists(conn, schema, table_name)
        if table_exists(conn.cursor(), schema, table_name):
            raise Exception(f"{table_name} table still exists")

        if 'movies_id' in column_names:
            raise Exception("The 'movies_id' column is not allowed because it's added automatically.")

        # remember to check the column names against the raw_movies table
        with conn.cursor() as cur:        
            # Create the new table from the columns of the raw_movies table
            create_table_query = sql.SQL("""
            CREATE TABLE {schema}.{table} AS
            SELECT {columns}, id AS movies_id
            FROM {schema}.raw_movies
            """).format(
                schema=sql.Identifier(schema),
                table=sql.Identifier(table_name),
                columns=sql.SQL(', ').join(sql.Identifier(col) for col in column_names)
            )
            logging.info(f"Executing create table query: {create_table_query.as_string(conn)}")
            cur.execute(create_table_query)
            
            # Add the foreign key constraint to movies_table.id named fk_table_name_movies
            add_foreign_key_query = sql.SQL("""
            ALTER TABLE {schema}.{table_name}
            ADD CONSTRAINT fk_{table_name}_movies
            FOREIGN KEY (movies_id) REFERENCES {schema}.{movies_table}(id)
            """).format(
                schema=sql.Identifier(schema),
                table=sql.Identifier(table_name),
                movies_table=sql.Identifier(movies_table)
            )
            logging.info(f"Executing add foreign key query: {add_foreign_key_query.as_string(conn)}")
            cur.execute(add_foreign_key_query)
            
    except Exception as e:
        logging.error(f"Error: {e}")
        conn.rollback()
        logging.info("Transaction rolled back.")
        raise


def drop_table_if_exists(conn, schema_name, table_name):
    """Drop a table from the specified schema."""
    try:
        with conn.cursor() as cur:
            drop_query = sql.SQL("""
            DROP TABLE IF EXISTS {schema}.{table}
            """).format(
                schema=sql.Identifier(schema_name),
                table=sql.Identifier(table_name)
            )
            logging.info(f"Executing drop query: {drop_query.as_string(conn)}")
            cur.execute(drop_query)
            conn.commit()
    except Exception as e:
        logging.error(f"Error: {e}")
        conn.rollback()
        logging.info("Transaction rolled back.")
        raise

def table_exists(cur, schema_name, table_name):
    """Check if a table exists in the specified schema."""
    select_exists_query = """
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables 
        WHERE table_schema = %s
        AND table_name = %s
    )
    """
    cur.execute(select_exists_query, (schema_name, table_name))
    result = cur.fetchone()[0]
    return result

def count_rows_in_table(cur, schema, table_name):
    """Return the number of rows in the table in the schema."""
    count_query = sql.SQL("""
    SELECT COUNT(*) FROM {schema}.{table}
    """).format(
        schema=sql.Identifier(schema),
        table=sql.Identifier(table_name)
    )
    cur.execute(count_query)
    result = cur.fetchone()[0]
    return result

def fetch_rows_and_columns(csv_file_path):
    """Fetch rows and column names from a CSV file."""
    try:
        rows = []
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            column_names = next(reader)
            for row in reader:
                rows.append(row)
        return column_names, rows
    except Exception as e:
        logging.error(f"Error: {e}")
        raise

def validate_columns(fetched_columns, expected_columns):
    """Validate fetched columns against expected columns."""
    if set(fetched_columns) != set(expected_columns):
        raise ValueError("CSV columns do not match the expected columns.")
    logging.info("CSV columns validated successfully.")
    

if __name__ == "__main__":

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    CURRENT_SCHEMA = 'patient_iq_schema'
    MOVIES_TABLE = 'raw_movies'
    META_MOVIES_CSV_PATH = '/Users/sbecker11/workspace-patient-iq/kaggle-movies-processor/movies_metadata.csv'
    EXPECTED_COLUMNS = [
        'adult', 'belongs_to_collection', 'budget', 'genres', 'homepage', 'id', 'imdb_id',
        'original_language', 'original_title', 'overview', 'popularity', 'poster_path',
        'production_companies', 'production_countries', 'release_date', 'revenue', 'runtime',
        'spoken_languages', 'status', 'tagline', 'title', 'video', 'vote_average', 'vote_count'
    ]
    
    conn = psycopg2.connect(
        dbname="patient_iq",
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host="localhost"
    )

    # SET UP THE DATABASE AND SCHEMA SEARCH PATH
    with conn.cursor() as cur:
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {CURRENT_SCHEMA}")
        logging.info(f"Schema {CURRENT_SCHEMA} created if needed.")
        schemaSearchPath = f"{CURRENT_SCHEMA}, public"
        cur.execute(f"SET search_path TO {schemaSearchPath}")
        logging.info(f"Schema search_path set to: {schemaSearchPath}.")
        conn.commit()
        
    # CREATE THE MOVIES TABLE, VALIDATE THE COLUMNS, AND INSERT 
    # THE ROWS INTO THE NEW MOVIES TABLE
    column_names, rows = fetch_rows_and_columns(META_MOVIES_CSV_PATH)
    validate_columns(column_names, EXPECTED_COLUMNS)
    
    create_fresh_movies_table(conn, CURRENT_SCHEMA, MOVIES_TABLE, rows, column_names)
    
    # CREATE THE COLUMN TABLES THAT REFERENCE THE MOVIES TABLE
    # create_fresh_column_table(conn, CURRENT_SCHEMA, 'genres', ['id','genre'], MOVIES_TABLE)
    # create_fresh_column_table(conn, CURRENT_SCHEMA, 'production_companies', ['id','production_company'], MOVIES_TABLE)
    # create_fresh_column_table(conn, CURRENT_SCHEMA, 'spoken_languages', ['id','spoken_language'], MOVIES_TABLE)
    
    conn.close()
    logging.info("Connection closed.")