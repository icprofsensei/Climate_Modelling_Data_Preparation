import os
import shutil
import json
import csv
import pandas as pd


def onlyalpha(s):
    t = ""
    for i in s:
        if i.isalpha():
            t += i
    return t

def upsert(folder, prefix, ac):
        WEATHER_DIR = f"C:/Users/Dhyla/Documents/Startup_Success/climastock2/{folder}"
        OUTPUT_DIR = "C:/Users/Dhyla/Documents/Startup_Success/climastock2"
        target = f"{WEATHER_DIR}/stations.txt"
        listening = 'off'
        data = [['STAID', 'STANAME','CN','LAT', 'LON', 'HGHT']]
        with open(target, encoding = 'latin-1') as f:
            for line in f:
                if line.startswith('STAID,'):
                    listening = 'on'
                elif listening == 'on':
                    linels = line.split(',')
                    linels = [l.strip() for l in linels]
                    data.append(linels)
                else:
                    continue
        headers = data.pop(0)
        targetdf = pd.DataFrame(data, columns=headers)

        target = f"{WEATHER_DIR}/sources.txt"
        listening = 'off'
        data2 = [['STAID', 'SOUID','SOUNAME','CN','LAT', 'LON', 'HGHT','ELEI','START','STOP','PARID','PARNAME','']]
        with open(target, encoding = 'latin-1') as f:
            for line in f:
                if line.startswith('STAID,'):
                    listening = 'on'
                elif listening == 'on':
                    linels = line.split(',')
                    linels = [l.strip() for l in linels]
                    data2.append(linels)
                else:
                    continue
        headers = data2.pop(0)
        target2df = pd.DataFrame(data2, columns=headers)


        print(target2df.head())
        filenames = [f for f in os.listdir(WEATHER_DIR) if f.endswith(('.txt'))]

        for f in filenames:
            noprefix = f.lstrip(f"{prefix}")
            nosuffix = str(noprefix.rstrip('.txt'))
            val = nosuffix.lstrip('0')
            print(val)
            if val.isdigit():
                row = targetdf.loc[targetdf['STAID'] == str(int(val))]
                if row.empty:
                    row = target2df.loc[target2df['STAID'] == str(int(val))]
                    station = onlyalpha(row['SOUNAME'].iloc[0])
                    cn = str(row['CN'].iloc[0]) 
                    staid = str(row['STAID'].iloc[0])
                else:
                    station = onlyalpha(row['STANAME'].iloc[0])
                    cn = str(row['CN'].iloc[0]) 
                    staid = str(row['STAID'].iloc[0])
                title = f"{staid}_{cn}_{station}_.csv"
                print(title)
                listening = 'off'
                data = [['STAID','SOUID','DATE',ac,f"Q_{ac}"]]
                file = f"{WEATHER_DIR}/{f}"
                newaddress = f"{WEATHER_DIR}/{title}"
                print(file, newaddress)
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
upsert('min_temp', 'TN_STAID', 'TX')