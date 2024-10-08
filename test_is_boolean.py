import pandas as pd

# Example DataFrame
data = {
    'adult': ['False', 'True', ' - Written by Ørnås', 
              ' Rune Balot goes to a casino connected to the October corporation to try to wrap up her case once and for all.',
              ' Avalanche Sharks tells the story of a bikini contest that turns into a horrifying affair when it is hit by a shark avalanche.'],
    'video': ['False', 'True', 'False', 'True', 'False'],
    'other': [False, True, False, True, None],
    'other2': [True, True, False, True, '']
}
df = pd.DataFrame(data)

# Define apply_func
def is_boolean(x):
    if isinstance(x, str):
        return x.lower() in ['true', 'false']
    return isinstance(x, bool)

# Define valid values
valid_values = ['true', 'false']

# Filter columns
apply_func = is_boolean
name = 'boolean'
skip_cols: list[str] = []
if valid_values:
    all_name_columns = [
        col for col in df.columns 
        if df[col].dropna().apply(apply_func).all() 
        and col not in skip_cols 
        and df[col].dropna().astype(str).str.lower().isin(valid_values).all()
    ]
else:
    all_name_columns = [
        col for col in df.columns 
        if df[col].dropna().apply(apply_func).all() 
        and col not in skip_cols 
        and df[col].dropna()
    ]
print(f"Columns with ALL boolean values (ignoring nulls): {all_name_columns}")


# Example DataFrame
data = {'column_name': ['True', 'False', 'True', 'False']}
df = pd.DataFrame(data, columns=['column_name'], dtype=str)

# force the column to be boolean, the map is applied to each element in the column
df['column_name'] = df['column_name'].map(lambda x: x == 'True')

print(df)