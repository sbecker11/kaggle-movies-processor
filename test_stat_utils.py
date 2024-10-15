from unittest import TestCase
import pandas as pd

from stat_utils import show_df_grid, show_duplicates

class TestStatUtils(TestCase):

    def test_titles(self):

        # Sample DataFrame
        data = {
            'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'Age': [25, 30, 25, 35, 30]
        }
        df = pd.DataFrame(data)

        print(f"{df['Name'].title_counts()}")
        print(f"{df['Age'].title_counts()}")
        
        for col in df.columns:
            top_3_col_title_counts = df[col].title_counts()[:12]
            print(f"Column: '{col}' top 3 unique title_counts:")
            print(top_3_col_title_counts)

    def test_column_names(self):
        
        with open("movies.csv", "r") as f:
            column_names = f.readline().split(',')
        for col in column_names:
            print(f"{col}")
    
    def test_show_duplicates(self):
        data = {
            'id': [451, 21, 21, 333, 333, 333, 4, 500, 500],
            'title': ['Alpha', 'Bravo', 'Bravo', 'Charlie', 'Charlie', 'Charlie', 'Delta', 'Echo', 'Echo']
        }
        df = pd.DataFrame(data)
        show_duplicates(df)
        
    def test_format_index_strings(self):
        df = pd.DataFrame({
            'Alphabet': ['abcdefghij', 'klmnopqrst', 'uvwxyzabcd', 'efghijklmn', 'klmnopqrst', 'uvwxyzabcd', 'efghijklmn', 'opqrstuvwx'],
            'Bandanas': ['1234567890', '0987654321', '1122334455', '5566778899', '0987654321', '1122334455', '5566778899', '0001112223'],
            'Coconuts': ['1234567890', '0987654321', '1122334455', '5566778899', '0987654321', '1122334455', '5566778899', '0001112223']
        })
        index_strings = [str(idx) for idx in df.index]
        print(index_strings)


    def test_show_df_grid(self):
        # Example usage:
        df = pd.DataFrame({
            'A': ['abcdefghij', 'klmnopqrst', 'uvwxyzabcd', 'efghijklmn', 'klmnopqrst', 'uvwxyzabcd', 'efghijklmn', 'opqrstuvwx'],
            'B': ['1234567890', '0987654321', '1122334455', '5566778899', '0987654321', '1122334455', '5566778899', '0001112223'],
            'C': ['1234567890', '0987654321', '1122334455', '5566778899', '0987654321', '1122334455', '5566778899', '0001112223'],
            'D': ['abcdefghij', 'klmnopqrst', 'uvwxyzabcd', 'efghijklmn', 'klmnopqrst', 'uvwxyzabcd', 'efghijklmn', 'opqrstuvwx'],
            'E': ['1234567890', '0987654321', '1122334455', '5566778899', '0987654321', '1122334455', '5566778899', '0001112223'],
            'F': ['1234567890', '0987654321', '1122334455', '5566778899', '0987654321', '1122334455', '5566778899', '0001112223'],
            'G': ['1234567890', '0987654321', '1122334455', '5566778899', '0987654321', '1122334455', '5566778899', '0001112223'],
            'H': ['1234567890', '0987654321', '1122334455', '5566778899', '0987654321', '1122334455', '5566778899', '0001112223'],
            'I': ['abcdefghij', 'klmnopqrst', 'uvwxyzabcd', 'efghijklmn', 'klmnopqrst', 'uvwxyzabcd', 'efghijklmn', 'opqrstuvwx'],
            'J': ['1234567890', '0987654321', '1122334455', '5566778899', '0987654321', '1122334455', '5566778899', '0001112223'],
            'K': ['1234567890', '0987654321', '1122334455', '5566778899', '0987654321', '1122334455', '5566778899', '0001112223'],
            'L': ['abcdefghij', 'klmnopqrst', 'uvwxyzabcd', 'efghijklmn', 'klmnopqrst', 'uvwxyzabcd', 'efghijklmn', 'opqrstuvwx']
        }, dtype='str')

        show_df_grid(df, N=3, truncate_length=5, index_width=3)