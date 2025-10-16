import os
import shutil
import json
import pandas as pd
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
from tqdm import tqdm

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
        self.root.geometry("800x300")
        self.weather_dir = ""
        self.output_dir = ""
        self.feature = ""
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
        if not self.weather_dir or not self.output_dir or not self.feature:
            messagebox.showwarning("Input Error: Complete all fields")
        else:
            self.feature = self.feature.get("1.0", tk.END).strip()
            try:
                self.root.destroy()
            except Exception as e:
                messagebox.showerror(f"Error {e} occurred")
    
    
    def create_widgets(self):
        inputlab = tk.Label(self.root, text= "Unzipped weather files")
        inputlab.pack(pady=5)
        self.inputloc = tk.Entry(self.root, width = 50)
        self.inputloc.pack(pady=5)
        inputbutton = tk.Button(self.root, text = "Browse", command = self.select_weather_zip)
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


#  LAUNCH GUI

root = tk.Tk()
app = LocatorApp(root)
root.mainloop()
WEATHER_DIR = app.weather_dir
OUTPUT_DIR = app.output_dir
feature = app.feature
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
            dataELE.append(linels)
        else:
            continue
headers = dataELE.pop(0)
targetdfELE = pd.DataFrame(dataELE, columns=headers)
targetdfELE.to_csv(f"{OUTPUT_DIR}/data-{prefix}-{feature}/elements.csv")

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
            dataSTA.append(linels)
        else:
            continue
headers = dataSTA.pop(0)
targetdfSTA = pd.DataFrame(dataSTA, columns=headers)
targetdfSTA.to_csv(f"{OUTPUT_DIR}/data-{prefix}-{feature}/stations.csv")

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
            if len(linels) != 12 and len(linels) >1:
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
targetdfSOU = pd.DataFrame(dataSOU, columns=headers)
targetdfSOU.to_csv(f"{OUTPUT_DIR}/data-{prefix}-{feature}/sources.csv")

#ITERATE

for f in tqdm(filenames):
    parts = f.split('_')
    if len(parts)>1:
        prefix = parts[0]
        middle = onlyalpha(parts[1])
    else:
        continue
    noprefix = f.split('_')[1].lstrip(f"{middle}")
    nosuffix = str(noprefix.rstrip('.txt'))
    val = nosuffix.lstrip('0')
    #print(val)
    if val.isdigit():
        row = targetdfSTA.loc[targetdfSTA['STAID'] == str(int(val))]
        if row.empty:
            row = targetdfSOU.loc[targetdfSOU['STAID'] == str(int(val))]
            station = onlyalpha(row['SOUNAME'].iloc[0])
            cn = str(row['CN'].iloc[0]) 
            staid = str(row['STAID'].iloc[0])
        else:
            station = onlyalpha(row['STANAME'].iloc[0])
            cn = str(row['CN'].iloc[0]) 
            staid = str(row['STAID'].iloc[0])
        title = f"{prefix}_{staid}_{cn}_{station}_.csv"
        listening = 'off'
        data = [['STAID','SOUID','DATE',prefix,f"Q_{prefix}"]]
        file = f"{WEATHER_DIR}/{f}"
        newaddress = f"{OUTPUT_DIR}/data-{prefix}-{feature}/{title}"
        with open(file, encoding = 'latin-1') as g:
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
        tempdf = pd.DataFrame(data, columns=headers)
        tempdf.to_csv(newaddress)
        os.remove(file)
