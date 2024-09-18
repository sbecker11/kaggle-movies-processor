# kaggle-movies-processor
original 238862293 byte zip file was downloaded to local disk from web page
https://www.kaggle.com/rounakbanik/the-movies-dataset/version/7#movies_metadata

The zip file was unzipped resulting in the following files:
189917659 credits.csv
  6231943 keywords.csv
   989107 links.csv
   183372 links_small.csv
 34445126 movies_metadata.csv
709550327 ratings.csv
  2438266 ratings_small.csv

The "movies_metadata_tables.csv" file has been
targeted for this project.

Preliminary data exploration loads the 
target csv file, "explore_movies_file.py",
into a pandas dataframe for initial data
exploration by the "explore_movies_file.py"
script. Once loaded, basic evalution reveals 
the following columns:
['adult', 'belongs_to_collection', 'budget', 'genres', 'homepage', 'id', 'imdb_id', 'original_language', 'original_title', 'overview', 'popularity', 'poster_path', 'production_companies', 'production_countries', 'release_date', 'revenue', 'runtime', 'spoken_languages', 'status', 'tagline', 'title', 'video', 'vote_average', 'vote_count']

Of these, the following columns have been identified for pre-processing:
['id', 'genres', 'production_companies', 'original_language']

Taking a random sample of a few rows from this dataset reveals the
nature of the values in these columns. For example,

Row 43526:
  id: '411405'
  genres: "[{'id': 18, 'name': 'Drama'}, {'id': 35, 'name': 'Comedy'}, {'id': 53, 'name': 'Thriller'}, {'id': 80, 'name': 'Crime'}]"
  production_companies: "[{'name': 'Rooks Nest Entertainment', 'id': 34456}]"
  original_language: 'en'
  ...

From this we conclude that datatypes for these 4 columns are:
    id: a quoted number
    genres: json-like value
    production_companies: json-like value
    original_language: a two-character language code

Preprocessing on the json-like columns requires the
a custom transformation: for example, given a JSON-like
string value:

    "[{'name': 'Rooks Nest Entertainment', 'id': 34456}]"

in order to tranform it into a python object, single quotes 
wrapping the key and possibly the value must be replaced 
with wrapping double quotes. For the example shown above, 
the original value must be transformed to this:

'[{"name": "Rooks Nest Entertainment", "id": 34456}]'

Simply swapping single-quotes for double quotes in the
original string is not sufficient. Special handling is 
required to handle cases where single or double quotes 
are found inside the wrapping quotes.

The parse_json_like_column function takes all values 
in a given column of the dataset and attempts to 
transform all values JSON-parsable strings before 
being parsed into Python objects.

If any part of a JSON-like value causes JSON parsing 
failure  the entire value will be logged as invalid 
and non-transformable before being replaced with a 
Python None value.
    
Row, column, and value causing any parse, syntax, or value 
errors are logged to an external 'bad_lines.txt' file.
A limit is placed on the number of errors logged to stdout.

After all preprocessing transformatinons have been applied
all columns, the updated dataframe is stored to the preprocessed 
csv file named  "movies_metadata_tables_preprocessed.csv" 

The next step is 

