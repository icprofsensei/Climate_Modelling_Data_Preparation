import pandas as pd 
import os
from csv import DictWriter
FILE_DIR = "c:/users/dhyla/documents/startup_success/climastock2/rain"
def getyear(val):
      year = val[0:4]
      year = int(year)
      return year
filenames = [f for f in os.listdir(FILE_DIR) if f.endswith(('.csv'))]
lennames = len(filenames)
sources = FILE_DIR + '/sources.txt'
listening = 'off'
data = [['STAID', 'SOUID', 'SOUNAME','CN','LAT', 'LON', 'HGHT', 'ELEI', 'START', 'STOP', 'PARID', 'PARNAME', '']]
with open(sources, encoding = 'latin-1') as f:
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
sourcesdf = pd.DataFrame(data, columns=headers)
sourcesdf['STOPYEAR'] = sourcesdf['STOP'].apply(getyear)
sourcesdf = sourcesdf.dropna(how='all')
germany = sourcesdf[sourcesdf['CN']=='DE']
germany = germany[germany['STOPYEAR'] == 2025]
germany = germany.drop_duplicates(subset=['SOUNAME'])
print(germany)
output_dir = 'c:/users/dhyla/documents/startup_success/climastock3'
with open(os.path.join(output_dir, 'raingermany.csv'), 'a', newline='') as f:
    writer = DictWriter(f, fieldnames=['lat', 'lon', 'height', 'date', 'daily_rainfall'])
    for i, f in enumerate(filenames):
            print(f"{i}/{lennames}")
            fileloc = sources = FILE_DIR + '/' + f
            locdet = f.split('_')
            country = locdet[1]
            station = locdet[2]
            match = germany.loc[(germany['SOUNAME']==station) & (germany['CN']==country)]
            if match.empty:
                match = germany.loc[germany['SOUID']==locdet[0] ]
                if match.empty:
                    match = germany.loc[germany['STAID']==locdet[0] ] 
                else:
                     continue
            if match.empty == False:
                LAT = match['LAT'].iloc[0]
                LON = match['LON'].iloc[0]
                HEIGHT = match['HGHT'].iloc[0]
                listening = 'off'
                df = pd.read_csv(fileloc)
                for index, row in df.iterrows():
                        if row['RR'] != -9999 and row['RR'] != '-9999':
                            writer.writerow({'lat': LAT, 'lon': LON, 'height': HEIGHT, 'date': row['DATE'],'daily_rainfall': row['RR']})