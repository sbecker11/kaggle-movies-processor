import pandas as pd
from functools import partial

# Example DataFrame
data = {
    'date_1': ['2022-10-11', '2024-11-03', '24-12-01', None],
    'date_2': ['2022-10-11', '2024-11-03', '24-12-01', '2013-01-01'],
    'date_3': ['', '2024-11-03T14:14:14.123=06:00', '2024-10-03T18:32:08 UTC', '2024-11-03']
}
df = pd.DataFrame(data)

print("Original Date Columns:")
print(df[['date_1', 'date_2', 'date_3']])

def is_datetime_str(x, format='%Y-%m-%d'):
    if isinstance(x, str) and len(x.strip()) > 0:
        try:
            pd.to_datetime(x, format=format)
            return True
        except ValueError:
            return False
    return False

# Create a partially applied function
is_datetime_str_yyyy_mm_dd = partial(is_datetime_str, format="%Y-%m-%d")

# Apply the partially applied function to each column
df['is_date_1'] = df['date_1'].map(is_datetime_str_yyyy_mm_dd)
df['is_date_2'] = df['date_2'].map(is_datetime_str_yyyy_mm_dd)
df['is_date_3'] = df['date_3'].map(is_datetime_str_yyyy_mm_dd)

print("\nBoolean Date Columns:")
print(df[['is_date_1', 'is_date_2', 'is_date_3']])
