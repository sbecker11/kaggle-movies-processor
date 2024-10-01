import pandas as pd

# Example DataFrame
data = {'column_name': ['True', 'False', 'True', 'False']}
df = pd.DataFrame(data, columns=['column_name'], dtype=str)

# force the column to be boolean, the map is applied to each element in the column
df['column_name'] = df['column_name'].map(lambda x: x == 'True')

print(df)