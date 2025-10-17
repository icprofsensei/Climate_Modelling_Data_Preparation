import os
import shutil
import json
import pandas as pd
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
from tqdm import tqdm
import polars as pl


# CHECK ONLY ALPHABETICAL CHARACTERS
def onlyalpha(s):
    t = ""
    for i in s:
        if i.isalpha():
            t += i
    return t


# TKINTER GUI

class LocatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title('File Selector')
        self.root.geometry("800x400")
        self.weather_dir = ""
        self.output_dir = ""
        self.selection = ""
        self.create_widgets()

    def select_weather_zip(self):
        self.weather_dir = filedialog.askdirectory(title = "Select the folder containing the unzipped weather files: ")
        if self.weather_dir:
            self.inputloc.delete(0, tk.END)
            self.inputloc.insert(0, self.weather_dir)
    
    def select_output_dir(self):
        self.output_dir = filedialog.askdirectory(title = "Select the folder where the csv files will be created: ")
        if self.output_dir:
            self.outputloc.delete(0, tk.END)
            self.outputloc.insert(0, self.output_dir)
    
    def submit(self):
        selection_val = self.selection.get()
        if not self.weather_dir or not self.output_dir or not selection_val:
            messagebox.showwarning("Input Error: Complete all fields")
        else:
            self.selection = selection_val
            try:
                self.root.destroy()
            except Exception as e:
                messagebox.showerror(f"Error {e} occurred")
    
    
    def create_widgets(self):
        inputlab = tk.Label(self.root, text= "Unzipped weather files")
        inputlab.grid(row=0, column = 1, pady=5)
        self.inputloc = tk.Entry(self.root, width = 50)
        self.inputloc.grid(row=1, column = 1, pady=5)
        inputbutton = tk.Button(self.root, text = "Browse", command = self.select_weather_zip)
        inputbutton.grid(row=2, column = 1, pady=5)

        outputlab = tk.Label(self.root, text= "Output directory")
        outputlab.grid(row=3, column = 1, pady=5)
        self.outputloc = tk.Entry(self.root, width = 50)
        self.outputloc.grid(row=4, column = 1, pady=5)
        outputbutton = tk.Button(self.root, text = "Browse", command = self.select_output_dir)
        outputbutton.grid(row=5, column = 1, pady=5)

        figtype = tk.Label(self.root, text = "What variable is being investigated?")
        figtype.grid(row=6, column = 1, pady=5)
        self.selection = tk.StringVar(value = "Image")
        frame = tk.Frame(self.root)
        frame.grid(row=6, column = 1,pady = 5)
        TX = tk.Radiobutton(self.root, text="Daily Maximum Temperature", variable=self.selection, value="DailyMaximumTemperature")
        TN= tk.Radiobutton(self.root, text="Daily Minimum Temperature", variable=self.selection, value="DailyMinimumTemperature")
        TG = tk.Radiobutton(self.root, text="Daily Mean Temperature", variable=self.selection, value="DailyMeanTemperature")
        RR = tk.Radiobutton(self.root, text="Daily Precipitation Amount", variable=self.selection, value="DailyPrecipitationAmount")
        PP = tk.Radiobutton(self.root, text="Daily Mean Sea Level Pressure", variable=self.selection, value="DailyMeanSeaLevelPressure")
        CC = tk.Radiobutton(self.root, text="Daily Cloud Cover", variable=self.selection, value="DailyCloudCover")
        HU = tk.Radiobutton(self.root, text="Daily Humidity", variable=self.selection, value="DailyHumidity")
        SD = tk.Radiobutton(self.root, text="Daily Snow Depth", variable=self.selection, value="DailySnowDepth")
        SS = tk.Radiobutton(self.root, text="Daily Sunshine Duration", variable=self.selection, value="DailySunshineDuration")
        QQ = tk.Radiobutton(self.root, text="Global Radiation", variable=self.selection, value="GlobalRadiation")
        FG = tk.Radiobutton(self.root, text="Daily Mean Wind Speed", variable=self.selection, value="DailyMeanWindSpeed")
        FX = tk.Radiobutton(self.root, text="Daily Maximum Wind Gust", variable=self.selection, value="DailyMaximumWindGust")
        DD = tk.Radiobutton(self.root, text="Daily Wind Direction", variable=self.selection, value="DailyWindDirection")
        TX.grid(row=7, column=1, sticky="w",padx=5)
        TN.grid(row=7, column=2, sticky="w",padx=5)
        TG.grid(row=7, column=3, sticky="w",padx=5)
        RR.grid(row=8, column=1, sticky="w",padx=5)
        PP.grid(row=8, column=2, sticky="w",padx=5)
        CC.grid(row=8, column=3, sticky="w",padx=5)
        HU.grid(row=9, column=1, sticky="w",padx=5)
        SD.grid(row=9, column=2, sticky="w",padx=5)
        SS.grid(row=9, column=3, sticky="w",padx=5)
        QQ.grid(row=10, column=1, sticky="w",padx=5)
        FG.grid(row=10, column=2, sticky="w",padx=5)
        FX.grid(row=10, column=3, sticky="w",padx=5)
        DD.grid(row=11, column=1, sticky="w",padx=5)

        submit_button = tk.Button(self.root, text = "Submit", command = self.submit)
        submit_button.grid(row=12, column=1, padx=5)


#  LAUNCH GUI

root = tk.Tk()
app = LocatorApp(root)
root.mainloop()
WEATHER_DIR = app.weather_dir
OUTPUT_DIR = app.output_dir
feature = app.selection
filenames = [f for f in os.listdir(WEATHER_DIR) if f.endswith(('.txt'))]
regfiles = [f for f in filenames if f.rstrip('.txt') not in ['date_timestamp', 'elements', 'sources', 'stations']]
prefix = regfiles[0].split('_')[0]
os.makedirs(f"{OUTPUT_DIR}/data-{prefix}-{feature}", exist_ok = True)

#ELEMENTS
target = f"{WEATHER_DIR}/elements.txt"
listening = 'off'
dataELE = [['ELEID', 'DESC']]
with open(target, encoding = 'latin-1') as f:
    for line in f:
        if line.startswith('ELEID,'):
            listening = 'on'
        elif listening == 'on':
            linels = line.split(',', 1)
            linels = [l.strip() for l in linels]
            if len(linels) > 1:
                dataELE.append(linels)
        else:
            continue
headers = dataELE.pop(0)
targetdfELE = pl.DataFrame(dataELE, schema=headers, orient="row")

targetdfELE.write_parquet(f"{OUTPUT_DIR}/data-{prefix}-{feature}/elements.parquet")

#STATIONS
target = f"{WEATHER_DIR}/stations.txt"
listening = 'off'
dataSTA = [['STAID', 'STANAME','CN','LAT', 'LON', 'HGHT']]
with open(target, encoding = 'latin-1') as f:
    for line in f:
        if line.startswith('STAID,'):
            listening = 'on'
        elif listening == 'on':
            linels = line.split(',')
            linels = [l.strip() for l in linels]
            if len(linels) > 1:
                dataSTA.append(linels)
        else:
            continue
headers = dataSTA.pop(0)
targetdfSTA = pl.DataFrame(dataSTA, schema=headers, orient = "row")
targetdfSTA.write_parquet(f"{OUTPUT_DIR}/data-{prefix}-{feature}/stations.parquet")

#SOURCES
target = f"{WEATHER_DIR}/sources.txt"
listening = 'off'
dataSOU = [['STAID', 'SOUID','SOUNAME','CN','LAT', 'LON', 'HGHT','ELEI','START','STOP','PARID','PARNAME']]
with open(target, encoding = 'latin-1') as f:
    for line in f:
        if line.startswith('STAID,'):
            listening = 'on'
        elif listening == 'on':
            linels = line.split(',')
            linels = [l.strip() for l in linels if l!= None]
            if len(linels) != 12:
                    if len(linels) <2:
                        continue
                    else:
                        sublist = linels[0:1]
                        sublist.append((linels[2]+'-'+ linels[3]))
                        sublist2 = linels[4:]
                        overall = sublist + sublist2
                        if type(overall[2]) == str and type(overall[6]) == int:
                                dataSOU.append(overall)
                        else:
                            continue
            else:
                linels = [l.strip() for l in linels if l!= None]
                dataSOU.append(linels)
        else:
            continue
headers = dataSOU.pop(0)
targetdfSOU = pl.DataFrame(dataSOU, schema=headers, orient = "row")
targetdfSOU.write_parquet(f"{OUTPUT_DIR}/data-{prefix}-{feature}/sources.parquet")

#ITERATE

for file in tqdm(filenames):
    parts = file.split('_')
    if len(parts)>1:
        prefix = parts[0]
        middle = onlyalpha(parts[1])
    else:
        continue
    noprefix = file.split('_')[1].lstrip(f"{middle}")
    nosuffix = str(noprefix.rstrip('.txt'))
    val = nosuffix.lstrip('0')
    if val.isdigit():
        
        title = f"{file}_{prefix}.parquet"
        listening = 'off'
        data = [['STAID','SOUID','DATE',prefix,f"Q_{prefix}"]]
        filead = f"{WEATHER_DIR}/{file}"
        newaddress = f"{OUTPUT_DIR}/data-{prefix}-{feature}/{title}"
        with open(filead, encoding = 'latin-1') as g:
            for line in g:
                if line.startswith('STAID,'):
                    listening = 'on'
                elif listening == 'on':
                    linels = line.split(',')
                    linels = [l.strip() for l in linels]
                    data.append(linels)
                else:
                    continue
        headers = data.pop(0)
        tempdf = pl.DataFrame(data, schema=headers, orient = "row")
        tempdf.write_parquet(newaddress)
        os.remove(filead)
