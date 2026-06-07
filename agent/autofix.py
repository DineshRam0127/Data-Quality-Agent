import pandas as pd

def auto_fix(df):

    # Fill missing names
    if "name" in df.columns:
        df["name"] = df["name"].fillna("Unknown")

    # Convert negative salary to positive
    if "salary" in df.columns:
        df["salary"] = df["salary"].abs()

    # Remove duplicate emails
    if "email" in df.columns:
        df = df.drop_duplicates(subset=["email"])

    return df