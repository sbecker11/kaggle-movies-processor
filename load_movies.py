import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Connect to the PostgreSQL database
engine = create_engine( os.getenv('POSTGRES_CONNECTION_URL') )

# Read the CSV file into a Pandas DataFrame
df = pd.read_csv(os.getenv('MOVIES_CSV_PATH'))

# Find rows with duplicate 'id' values
duplicate_ids = df[df.duplicated('id', keep=False)]['id']
print(f"number of rows with duplicate 'id' values: {len(duplicate_ids.tolist())}")

# for each set of duplicate rows, count the number of duplicate column values
for id in duplicate_ids:
    print(f"Number of duplicate rows for id {id}: {len(df[df['id'] == id])}")
    # count the number of columns that match the first row of the set of duplicate rows
    # also count the number of columns that don't match the first row of the set of duplicate rows
    duplicate_rows = df[df['id'] == id]
    for col in df.columns:
        duplicate_values = duplicate_rows[col].duplicated(keep=False).sum()
        different_values = len(duplicate_rows) - duplicate_values
        print(f"Number of duplicate values in column {col}: {duplicate_values}")
        print(f"Number of different values in column {col}: {different_values}")

# Create a new DataFrame with only the duplicate rows
duplicate_ids_df = df[df['id'].isin(duplicate_ids)]

# Write the duplicate rows to a new CSV file
duplicate_ids_df.to_csv('/Users/sbecker11/workspace-dbt/dbt-postgresql/movies_metadata_duplicate_ids.csv', index=False)

# Drop the duplicate rows from the original DataFrame
print(f"Number of rows before dropping duplicates: {len(df)}")
df = df[~df['id'].isin(duplicate_ids)]
print(f"Number of rows after dropping duplicates: {len(df)}")

# Find columns with missing data
missing_cols = df.columns[df.isna().any()].tolist()
print(f"Columns with missing data: {missing_cols}")

# find missing columns and fill with 0
for col in missing_cols:
    print(f"Missing data in column {col}: {df[col].isna().sum()}")  
    df[col] = df[col].fillna('0')

# list the unique values for each column and identify outier values in each column
df_outliers = pd.DataFrame()
for col in df.columns:
    print(f"Unique values in column {col}: {df[col].unique()}")
    # use a percentage threshold to identify outliers
    # calculate threashold by std deviation from mean > 3 std deviations
    threshold = 3 * df[col].std()
    mean = df[col].mean()
    
    # find the outliers in the column
    outliers_df = df[(df[col] - mean).abs() > threshold]
    print(f"Outlier values in column {col}: {outliers_df[col]} compared to mean: {mean} and threshold: {threshold}")

    # at the risk of adding bias to the data, Winsorize the outliers by clamping their distance to the threshold
    df.loc[(df[col] - mean) > threshold, col] = mean + threshold
    df.loc[(df[col] - mean) < -threshold, col] = mean - threshold
    
    # find columns that have json-like structured values that have format [{section1},{section2},...,{sectionN}]
    # then flatten the json-like structured values into a new DataFrame with two columns:
    # "movie_id" for the movie_id of that row in one column, and a "section" column that contains the 
    # exploded list of sections in the orginal value of the column for that row.
    if df[col].str.contains(r'\[.*\{.*\}.*\]').any():
        # create a new dataframe for this column and then drop this columrn from ther original dataframe
        col_df = pd.DataFrame(columns=['movie_id', 'section'])
        print(f"Column {col} contains json-like structured values")
        # extract the movie_id from the 'id' column
        col_df['movie_id'] = df['id']
        # extract the section values from the column (retain the curly braces)
        col_df['section'] = df[col].str.extractall(r'\{.*?\}').unstack().apply(lambda x: ','.join(x.dropna()), axis=1)
        # create the new csv for this column
        col_df.to_csv(f'/Users/sbecker11/workspace-dbt/dbt-postgresql/{col}_sections.csv', index = False)
        # drop the original column from the dataframe to avoid redundancy
        df = df.drop(columns=[col])
    
    

# Create the table in the database
df.to_sql('movies', engine, schema='dbt_schema', if_exists='replace', index=False)
