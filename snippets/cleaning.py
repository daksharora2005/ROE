import pandas as pd

# Handle missing values
def clean_missing_values(df):
    return df.fillna(method="ffill").fillna(method="bfill")

# Convert column types
def convert_column_types(df, column, dtype):
    df[column] = df[column].astype(dtype)
    return df

# Standardize column names
def standardize_column_names(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df
