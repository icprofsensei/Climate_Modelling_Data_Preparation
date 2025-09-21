import os
import shutil
import json
import csv
import tkinter as tk


WEATHER_DIR = "C:/Users/Dhyla/Documents/Startup_Success/climastock/ECA_blend_tx"
refjson = "C:/Users/Dhyla/Documents/Startup_Success/climastock/aaweathercountries.json"
OUTPUT_DIR = "C:/Users/Dhyla/Documents/Startup_Success/climastock"
filenames = [f for f in os.listdir(WEATHER_DIR) if f.endswith(('.txt'))]
with open(refjson, 'r') as file:
    data = json.load(file)

# Print the data
country_ids = [str(d['id']) for d in data]
totalobj = [str(d['name'])+'_'+str(d['country'])+'_'+str(d['id']) for d in data]
print(totalobj)
filestoquery = []
valls = []
for f in filenames:
    noprefix = f.lstrip('TX_STAID')
    nosuffix = str(noprefix.rstrip('.txt'))
    val = nosuffix.lstrip('0')
    if val in country_ids:
        filestoquery.append(f)
        valls.append(val)
os.makedirs(f"{OUTPUT_DIR}/data", exist_ok = True)
for fil in filestoquery:
    noprefix = fil.lstrip('TX_STAID')
    nosuffix = str(noprefix.rstrip('.txt'))
    val = nosuffix.lstrip('0')
    address = f'{WEATHER_DIR}/{fil}'
    listening = 'off'
    data = [['STAID','SOUID','DATE','TX','Q_TX']]
    with open(address) as f:
        for line in f:
            if line.startswith('STAID,'):
                print(line)
                listening = 'on'
            elif listening == 'on':
                linels = line.split(',')
                linels = [l.strip() for l in linels]
                data.append(linels)
            else:
                continue
    for to in totalobj:
        tols = to.split('_')
        if tols[2] == val:
            title = tols[0] + '_' + tols[1]
    with open(f"C:/Users/Dhyla/Documents/Startup_Success/climastock/data/{title}.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for d in data:
            writer.writerow(d)
