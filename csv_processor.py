import pandas as pd
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

# ------- TKINTER GUI ---------

class LocatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title('File Selector')
        self.root.geometry("800x300")
        self.weather_dir = ""
        self.output_dir = ""
        self.feature = ""
        self.create_widgets()

    def select_weather_file(self):
        self.weather_dir = filedialog.askopenfilename(title = "Select the file containing the csv weather file to investigate: ")
        if self.weather_dir:
            self.inputloc.delete(0, tk.END)
            self.inputloc.insert(0, self.weather_dir)
    
    def select_output_dir(self):
        self.output_dir = filedialog.askdirectory(title = "Select the folder where any output files will be created: ")
        if self.output_dir:
            self.outputloc.delete(0, tk.END)
            self.outputloc.insert(0, self.output_dir)
    
    def submit(self):
        
        if not self.weather_dir or not self.output_dir or not self.feature:
            messagebox.showwarning("Input Error: Complete all fields")
        else:
            self.feature = self.feature.get("1.0", tk.END).strip()
            try:
                self.root.destroy()
            except Exception as e:
                messagebox.showerror(f"Error {e} occurred")
    
    
    def create_widgets(self):
        inputlab = tk.Label(self.root, text= "Weather csv file:")
        inputlab.pack(pady=5)
        self.inputloc = tk.Entry(self.root, width = 50)
        self.inputloc.pack(pady=5)
        inputbutton = tk.Button(self.root, text = "Browse", command = self.select_weather_file)
        inputbutton.pack(pady=5)

        outputlab = tk.Label(self.root, text= "Output directory")
        outputlab.pack(pady=5)
        self.outputloc = tk.Entry(self.root, width = 50)
        self.outputloc.pack(pady=5)
        outputbutton = tk.Button(self.root, text = "Browse", command = self.select_output_dir)
        outputbutton.pack(pady=5)

        featurelab = tk.Label(self.root, text= "Feature: ")
        featurelab.pack(pady=5)
        self.feature = tk.Text(self.root, width = 50, height = 1)
        self.feature.pack(pady = 5)

        submit_button = tk.Button(self.root, text = "Submit", command = self.submit)
        submit_button.pack(pady=5)

# ------  PROCESSING -------

# STR TO DATE OBJ

def datecreator(strobj):
        strobj = str(strobj)
        y = int(strobj[0:4])
        m = int(strobj[4:6])
        d = int(strobj[6:8])
        dateobj = datetime.datetime(y,m,d)
        return dateobj

# DATA CLEANING PIPELINE

def pipeline(WEATHER_DIR):
    folderls = WEATHER_DIR.split('/')
    file = (folderls[len(folderls) - 1]).rstrip('.csv')
    feature = folderls[len(folderls) - 2 ]
    prefixbroken = feature.split('-')
    prefix = prefixbroken[len(prefixbroken) - 1]
    
    df = pd.read_csv(WEATHER_DIR)
    cols = list(df.columns)
    toremove = [c for c in cols if c.startswith("Unnamed")]
    df = df.drop(toremove, axis = 1)
    df = df[df[prefix] != -9999.0] 
    df['TRUEDATE'] = (df['DATE']).apply(datecreator)
    df['YEAR'] = df['TRUEDATE'].apply(lambda x: x.year)
    df['MONTH'] = df['TRUEDATE'].apply(lambda x: x.month)
    df['DAY'] = df['TRUEDATE'].apply(lambda x: x.day)
    df['DATE'] = df['TRUEDATE'].apply(lambda x: x.toordinal())
    df['MOVING_AVG_10'] = df[prefix].rolling(window = 10, center = True).mean()
    df['MOVING_AVG_30'] = df[prefix].rolling(window = 30, center = True).mean()
    df['Z_SCORE'] =  np.abs(stats.zscore(df[prefix]))
    return df, prefix, file

# INDIVIDUAL DATE MODELS

def dateextraction(df, prefix):
    DATELS = list(df['TRUEDATE'])
    md = list(set([d.strftime('%m-%d') for d in DATELS]))
    dates = {key: {} for key in md}
    df['MD'] = df['TRUEDATE'].apply(lambda x: x.strftime('%m-%d'))
    for k,v in dates.items():
        subdf = df[df['MD'] == k]
        model = LinearRegression()
        model.fit(np.array(subdf['DATE']).reshape((-1, 1)), np.array(subdf[prefix]))
        slope = model.coef_[0]
        dates[k]['intercept'] = float(model.intercept_)
        dates[k]['slope'] = slope
        '''subdf['EXP'] = (dates[k]['slope'] * subdf['DATE']) + dates[k]['intercept']
        dates[k]['df'] = subdf'''
    return dates

# LINEAR COEFFICIENT HISTOGRAM

def plot_coef_dist(datedict, path, feature):
    data = [v['slope'] for k,v in datedict.items()]
    kde_md = sns.kdeplot(data, bw_method = .2, fill=True, color="#27dcb8")
    kde_md.axvline(0)
    kde_md.set_xlabel('Slope coefficient for all days')
    kde_md.set_ylabel('Frequency')
    kde_md.set_title(f"Frequency Density Plot for {feature} across all years")
    plt.savefig(f"{path}/kde_md_coefficients.png")
    plt.close()

# 10 DAY MOVING AVG

def plot_10_avg(df, path, feature):
    outliers = df['Z_SCORE'] > 3
    outlier_indices = df[outliers].index
    df = df.drop(outlier_indices)
    df = df.sort_values('TRUEDATE')
    avg10 = sns.lineplot(df, x = 'TRUEDATE', y = 'MOVING_AVG_10', color = "#74ee84")
    avg10.set_xlabel('Date')
    avg10.set_ylabel(feature)
    avg10.set_title(f"Line Chart for {feature} across all years using a 10 day moving average")
    plt.savefig(f"{path}/10_day_moving_avg.png")
    plt.close()


# 30 DAY MOVING AVG

def plot_30_avg(df, path, feature):
    outliers = df['Z_SCORE'] > 3
    outlier_indices = df[outliers].index
    df = df.drop(outlier_indices)
    df = df.sort_values('TRUEDATE')
    avg30 = sns.lineplot(df, x = 'TRUEDATE', y = 'MOVING_AVG_30', color = "#cdee74")
    avg30.set_xlabel('Date')
    avg30.set_ylabel(feature)
    avg30.set_title(f"Line Chart for {feature} across all years using a 30 day moving average")
    plt.savefig(f"{path}/30_day_moving_avg.png")
    plt.close()

# RAW

def plot_raw(df, path, feature, prefix):
    outliers = df['Z_SCORE'] > 3
    outlier_indices = df[outliers].index
    df = df.drop(outlier_indices)
    df = df.sort_values('TRUEDATE')
    raw = sns.lineplot(df, x = 'TRUEDATE', y = prefix, color = "#cdee74")
    raw.set_xlabel('Date')
    raw.set_ylabel(feature)
    raw.set_title(f"Line Chart for {feature} across all years")
    plt.savefig(f"{path}/raw.png")
    plt.close()

#  LAUNCH GUI

root = tk.Tk()
app = LocatorApp(root)
root.mainloop()
WEATHER_DIR = app.weather_dir
OUTPUT_DIR = app.output_dir
feature = app.feature
df, prefix, file = pipeline(WEATHER_DIR)
datedict = dateextraction(df,  prefix)
result_dir = f"{OUTPUT_DIR}/RESULT-{file}"
os.makedirs(result_dir, exist_ok = True)
plot_coef_dist(datedict, result_dir, feature)
plot_10_avg(df, result_dir, feature)
plot_30_avg(df, result_dir, feature)
plot_raw(df, result_dir, feature, prefix)