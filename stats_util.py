import pandas as pd

def show_column_stats(df, col):
    if df[col].dtype == 'object':
        print(f"Column: {col} is of type 'object'")
        print(f"  Unique Values: {df[col].unique()}")
        print(f"  Value Counts: {df[col].value_counts()}")
        return
    
    mean = df[col].mean()
    median = df[col].median()
    mode = df[col].mode().iloc[0]
    std_dev = df[col].std()
    skew = df[col].skew()
    kurtosis = df[col].kurtosis()
    z_scores = np.abs(stats.zscore(df[col]))
    min_val = df[col].min()
    max_val = df[col].max()
    range_val = max_val - min_val
    variance = df[col].var()
    iqr = df[col].quantile(0.75) - df[col].quantile(0.25)
    missing_count = df[col].isnull().sum()
    unique_count = df[col].nunique()

    print(f"Column: {col}")
    print(f"  Mean: {mean}")
    print(f"  Median: {median}")
    print(f"  Mode: {mode}")
    print(f"  Standard Deviation: {std_dev}")
    print(f"  Skewness: {skew}")
    print(f"  Kurtosis: {kurtosis}")
    print(f"  Z-scores: {z_scores}")
    print(f"  Minimum: {min_val}")
    print(f"  Maximum: {max_val}")
    print(f"  Range: {range_val}")
    print(f"  Variance: {variance}")
    print(f"  Interquartile Range (IQR): {iqr}")
    print(f"  Missing Values Count: {missing_count}")
    print(f"  Unique Values Count: {unique_count}")

# Compare the effect of different scalers on the data of the given numeric column in the DataFrame
def compare_numeric_scalers(df, col, threshold=3):
    # Step 1: Apply StandardScaler
    standard_scaler = StandardScaler()
    df_standard_scaled = pd.DataFrame(
        standard_scaler.fit_transform(df), columns=df.columns)

    # Step 2: Apply Clamp or Drop Outliers
    df_standard_scaled_clamped = df_standard_scaled.clip(
        lower=-threshold, upper=threshold)
    df_standard_scaled_dropped = df_standard_scaled[(
        df_standard_scaled.abs() <= 3).all(axis=1)]

    # Step 3: Apply MinMaxScaler
    min_max_scaler = MinMaxScaler()
    df_min_max_scaled_clamped = pd.DataFrame(min_max_scaler.fit_transform(
        df_standard_scaled_clamped), columns=df.columns)
    df_min_max_scaled_dropped = pd.DataFrame(min_max_scaler.fit_transform(
        df_standard_scaled_dropped), columns=df.columns)

    # Print results
    show_column_stats(df, col + ' (Original):')
    show_column_stats(df_standard_scaled_clamped, col +
                      " (Standard Scaled Data (Clamped):")
    show_column_stats(df_min_max_scaled_clamped, col +
                      " (MinMax Scaled Data (Clamped):")
    show_column_stats(df_standard_scaled_dropped, col +
                      " (Standard Scaled Data (Dropped):")
    show_column_stats(df_min_max_scaled_dropped, col +
                      " (MinMax Scaled Data (Dropped):")

