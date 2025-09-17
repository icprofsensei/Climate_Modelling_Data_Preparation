import os
import shutil
import json
import csv
import pandas as pd
import numpy as np
import datetime
from sklearn.linear_model import LinearRegression
def datecreator(strobj):
        strobj = str(strobj)
        y = int(strobj[0:4])
        m = int(strobj[4:6])
        d = int(strobj[6:8])
        dateobj = datetime.datetime(y,m,d)
        return dateobj
WEATHER_DIR = "C:/Users/Dhyla/Documents/Startup_Success/climastock/ECA_blend_tx"
filenames = [f for f in os.listdir(WEATHER_DIR) if f.endswith(('.txt')) and f.startswith('TX')]
pointls = []
for address in filenames:
    print(address)
    full = WEATHER_DIR + '/' + address
    data = []
    headers = ['STAID','SOUID','DATE','TX','Q_TX']
    with open(full, encoding = 'utf-8') as f:
        listening = 'off'
        
        for line in f:
            row = {}
            if line.startswith('STAID,'):
                listening = 'on'
            elif listening == 'on':
                linels = line.split(',')
                linels = [int(str(l.strip())) for l in linels]
                for k, v in zip(headers, linels):
                    row[k]=v
                data.append(row)
            else:
                continue
    df = pd.DataFrame(data)
    
    df1 = df.drop(['STAID', 'SOUID', 'Q_TX'], axis = 1)
    df2 = df1[df1.TX != -9999]
    df2['DATE'].apply(lambda x: datecreator(x))
    model = LinearRegression()
    model.fit(np.array(df2['DATE']).reshape((-1, 1)), np.array(df2['TX']))
    r_sq = model.score(np.array(df2['DATE']).reshape((-1, 1)), np.array(df2['TX']))
    slope = model.coef_[0]
    point = {'correlation':slope, 'coefficient of determination': r_sq}
    pointls.append(point)
pointdf = pd.DataFrame(pointls)
pointdf.to_csv("C:/Users/Dhyla/Documents/Startup_Success/climastock/coefficients.csv")