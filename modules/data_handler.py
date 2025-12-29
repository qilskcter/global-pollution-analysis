import pandas as pd
import glob
import os
import streamlit as st

@st.cache_data
def process_air_data(file_source):
    df = pd.read_csv(file_source)
    df = df.interpolate(method='linear').ffill().bfill()
    if 'AQI Value' in df.columns:
        Q1 = df['AQI Value'].quantile(0.25)
        Q3 = df['AQI Value'].quantile(0.75)
        IQR = Q3 - Q1
        df = df[(df['AQI Value'] >= (Q1 - 1.5 * IQR)) & (df['AQI Value'] <= (Q3 + 1.5 * IQR))]
    return df

def find_all_csv():
    return glob.glob("*.csv") + glob.glob("**/*.csv", recursive=True)