import pandas as pd

def apply_higgons_filter(df):
    return df[
        (df["PER"] < 12) &
        (df["ROE (%)"] > 10) &
        (df["Revenue Growth (%)"] > 0)
    ]