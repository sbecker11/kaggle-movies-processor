from unittest import TestCase
import pandas as pd

from stat_utils import show_df_grid

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
            print(f"Column:{col} top 3 unique title_counts:")
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
        self.show_duplicates(df)

    def show_duplicates(self, df):
        
        dups_mask = df.duplicated(subset=['id', 'title'], keep=False)

        # Use the mask and keep the 'id' and 'title' columns of duplicate rows
        df = df.loc[dups_mask, ['id', 'title']]

        # Add the count of rows for each grouping of id
        df['count'] = df.groupby('id')['id'].transform('count')

        # Add a rank column for each grouping of id using the rank method
        df['rank'] = df.groupby('id').cumcount() + 1
        
        # # Keep only rows with rank 1
        df = df[df['rank'] == 1].drop(columns=['rank'])
        
        print("\nkeeping only rows with rank=1 and dropping rank column")
        print(df)


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