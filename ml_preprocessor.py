import pandas as pd
import polars as pl
import os
import matplotlib.pyplot as plt
import datetime
from sklearn.linear_model import LinearRegression
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from tqdm import tqdm
import seaborn as sns
from scipy import stats
import duckdb as ddb
from sqlalchemy import Column, Integer, Sequence, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session
from processor import PROCESS
from summarise import FIELDS
# ------- TKINTER GUI ---------

class LocatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title('File Selector')
        self.root.geometry("800x300")
        self.weather_dir = ""
        self.output_dir = ""
        self.create_widgets()

    def select_weather_folder(self):
        self.weather_dir = filedialog.askdirectory(title = "Select the folder containing the parquet weather file to preprocess: ")
        if self.weather_dir:
            self.inputloc.delete(0, tk.END)
            self.inputloc.insert(0, self.weather_dir)
    
    def select_output_dir(self):
        self.output_dir = filedialog.askdirectory(title = "Select the folder where your duck db database will be created: ")
        if self.output_dir:
            self.outputloc.delete(0, tk.END)
            self.outputloc.insert(0, self.output_dir)
    
    def submit(self):
        if not self.weather_dir or not self.output_dir:
            messagebox.showwarning("Input Error: Complete all fields")
        else:
            try:
                self.root.destroy()
            except Exception as e:
                messagebox.showerror(f"Error {e} occurred")
    
    
    def create_widgets(self):
        inputlab = tk.Label(self.root, text= "Weather csv file:")
        inputlab.grid(row=0, column = 1)
        self.inputloc = tk.Entry(self.root, width = 50)
        self.inputloc.grid(row=1, column = 1)
        inputbutton = tk.Button(self.root, text = "Browse", command = self.select_weather_folder)
        inputbutton.grid(row=2, column = 1)

        outputlab = tk.Label(self.root, text= "Output directory")
        outputlab.grid(row=3, column = 1)
        self.outputloc = tk.Entry(self.root, width = 50)
        self.outputloc.grid(row=4, column = 1)
        outputbutton = tk.Button(self.root, text = "Browse", command = self.select_output_dir)
        outputbutton.grid(row=5, column = 1)

        submit_button = tk.Button(self.root, text = "Submit", command = self.submit)
        submit_button.grid(row=6, column = 1)

def latlon_polars(col_series):
    # Cast the entire series to string at the beginning
    str_series = col_series.cast(pl.Utf8)
    
    split_data = str_series.str.split(':')
    degrees = split_data.list.get(0).cast(pl.Float64)
    minutes = split_data.list.get(1).cast(pl.Float64)
    seconds = split_data.list.get(2).cast(pl.Float64)
    sign = pl.when(str_series.str.starts_with('-')).then(-1).otherwise(1)
    decimal_degrees = sign * (degrees.abs() + minutes/60.0 + seconds/3600.0)
    return decimal_degrees.round(6)

root = tk.Tk()
app = LocatorApp(root)
root.mainloop()
WEATHER_DIR = app.weather_dir
OUTPUT_DIR = app.output_dir
duckdb_path = f"{OUTPUT_DIR}/weather.db"
featurels = WEATHER_DIR.split('/')
items = len(featurels)
feature = featurels[items -1].split('-')[1]
feature_name = featurels[items-1].split('-')[2]
schema = {
    'STAID': pl.Int64,
    'SOUID': pl.Int64, 
    'SOUNAME': pl.Utf8,
    'CN': pl.Utf8,
    'LAT': pl.Utf8,  
    'LON': pl.Utf8, 
    'HGHT': pl.Float64,
    'ELEI': pl.Utf8,
    'START': pl.Utf8, 
    'STOP': pl.Utf8
}
print("Making Database")
con = ddb.connect(database=duckdb_path, read_only=False) 
df_sources = pl.scan_parquet(f"{WEATHER_DIR}/sources.parquet", schema_overrides = schema)
sources = (df_sources.select(['STAID', 'SOUID', 'SOUNAME', 'CN', 'LAT', 'LON', 'HGHT', 'ELEI', 'START', 'STOP'])
           .with_columns([
                            pl.col("START").str.strptime(pl.Date, "%Y%m%d"),
                            pl.col("STOP").str.strptime(pl.Date, "%Y%m%d"),
                            latlon_polars(pl.col('LAT')).alias('LAT'),
                            latlon_polars(pl.col('LON')).alias('LON')
                        ])
           .collect())
con.execute(f"""
            CREATE TABLE IF NOT EXISTS {feature_name}_sources (
            STAID INTEGER, 
            SOUID INTEGER,
            SOUNAME VARCHAR,
            CN VARCHAR(3),
            LAT DECIMAL,
            LON DECIMAL, 
            HGHT INTEGER, 
            ELEI VARCHAR(8),
            START DATE,
            STOP DATE
            );
            INSERT INTO {feature_name}_sources
            SELECT * FROM sources;
""")
print("Loaded Sources")
df_stations = pl.scan_parquet(f"{WEATHER_DIR}/stations.parquet")
stations = (df_stations.select(['STAID',  'STANAME', 'CN', 'LAT', 'LON', 'HGHT'])
            .with_columns([latlon_polars(pl.col('LAT')).alias('LAT'),
                            latlon_polars(pl.col('LON')).alias('LON')
                        ])
            .collect())
con.execute(f"""
            CREATE TABLE IF NOT EXISTS {feature_name}_stations (
            STAID INTEGER, 
            STANAME VARCHAR,
            CN VARCHAR(3),
            LAT DECIMAL,
            LON DECIMAL, 
            HGHT INTEGER
            );
            INSERT INTO {feature_name}_stations
            SELECT * FROM stations;
""")
print("Loaded Stations")
df_elements = pl.scan_parquet(f"{WEATHER_DIR}/elements.parquet")
elements = (df_elements.select(['ELEID', 'DESC'])
            .rename({
                    "ELEID": "ELEID",
                    "DESC": f"{feature_name}_DESC"
                })
                .collect())
con.execute(f"""
            CREATE TABLE IF NOT EXISTS {feature_name}_elements (
            ELEID VARCHAR,
            {feature_name}_DESC VARCHAR
            );
            INSERT INTO {feature_name}_elements
            SELECT * FROM elements;
""")
print("Loaded Elements")
print("Reading feature files...")
df_overall = pl.scan_parquet(f"{WEATHER_DIR}/*_{feature}.csv")
result = (df_overall
          .filter(pl.col(feature) != -9999.0)
          .with_columns([
                            pl.col("DATE").cast(pl.Utf8).str.strptime(pl.Date, "%Y%m%d")
                        ])
          .collect())

con.execute(f"""
        CREATE TABLE IF NOT EXISTS {feature_name} (
        PK_{feature} INTEGER,
        STAID INTEGER,
        SOUID INTEGER, 
        DATE DATE, 
        HU INTEGER,
        Q_HU INTEGER) ;
        INSERT INTO {feature_name}
        SELECT * FROM result;
    """)
print("Finished")
FIELDS(duckdb_path, feature_name).show()
