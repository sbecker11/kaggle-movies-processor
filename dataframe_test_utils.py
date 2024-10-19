import pandas as pd
from typing import Dict, List, Any, Callable

# Define a new type alias
DataDict = Dict[str, List[Any]]
# Define a new type alias for the extractor function
ExtractorFunction = Callable[[Any], Any]

class DataFrameTestUtils:
        
    def show_df_values(self, name: str, df: pd.DataFrame):
        for col in df.columns:
            for row in range(len(df)):
                print(f"{name} col: {col} row: {row} : {df[col].iloc[row]}")

    def df_compare_shapes(self, name1: str, df1: pd.DataFrame, name2: str, df2: pd.DataFrame):
        num_diffs = 0
        if df1.shape != df2.shape:
            print(f"shapes of {name1} and {name2} should equal")
            num_diffs += 1
        if df1.columns.tolist() != df2.columns.tolist():
            print(f"columns of {name1} and {name2} should equal")
            num_diffs += 1
        if len(df1) != len(df2):
            print(f"rows of {name1} and {name2} should equal")
            num_diffs += 1
        return num_diffs

    def dfs_test_extractor(self, test_name: str, data_input: DataDict, data_expected: DataDict, column_type_extractor: ExtractorFunction, verbose: bool = False) -> None:
        df_input = pd.DataFrame(data_input)
        df_expected = pd.DataFrame(data_expected)
        df_result = df_input.map(column_type_extractor)
        diffs = 0
        diffs += self.df_compare_shapes("df_input", df_input, "df_expected", df_expected)
        diffs += self.df_compare_shapes("df_input", df_input, "df_result", df_result)
        self.assertEqual(0, diffs, "all dfs should have same shape")

        if verbose:
            print('=' * 80)
            print(test_name)
        
            print("df_input:------------------------------------")
            self.show_df_values("df_input", df_input)
            
            print("df_expected:---------------------------------")
            self.show_df_values("df_expected", df_expected)
            
            print("df_result:---------------------------------")
            self.show_df_values("df_result", df_result)
        
            print("df_differences:------------------------------")
            
        num_diff = self.show_df_differences(df_expected, df_result)
        self.assertEqual(0, num_diff, "there should be no differences between expected and result")
        
    # outputs the differences between df_exp and df_rst
    # and return the number of differences
    def show_df_differences(self, df_exp, df_rst):
        num_differences = 0
        for col in df_exp.columns:
            for row in range(len(df_exp)):
                val_exp = df_exp[col].iloc[row]
                val_rst = df_rst[col].iloc[row]
                if val_exp != val_rst:
                    num_differences += 1
                    print(f"Difference at col: {col} row: {row} - expected: {val_exp}, result: {val_rst}")
        return num_differences

    def assertEqual(self, a: Any, b: Any, msg: str = None):
        if a != b:
            self.fail(msg or f"{a} != {b}")
            
    def fail(self, msg: str):
        print(f"Error: {msg}")


# Example usage
if __name__ == "__main__":
    
    def extract_value(x: Any) -> Any:
        # Example implementation that returns the input value unchanged
        return x
    
    utils = DataFrameTestUtils()
    data_input = {
        'A': [1, 2, 3],
        'B': ['x', 'y', 'z']
    }
    data_expected = {
        'A': [1, 2, 4],  # Note the difference here
        'B': ['x', 'y', 'w']  # And here
    }
    utils.dfs_test_extractor("Test Case 1", data_input, data_expected, extract_value)