import pandas as pd
import os
import matplotlib.pyplot as plt
import datetime
from sklearn.linear_model import LinearRegression
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from tqdm import tqdm


# TKINTER GUI

class LocatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title('File Selector')
        self.root.geometry("800x300")
        self.weather_dir = ""
        self.output_dir = ""
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
        if not self.weather_dir or not self.output_dir:
            messagebox.showwarning("Input Error: Complete all fields")
        else:
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

        submit_button = tk.Button(self.root, text = "Submit", command = self.submit)
        submit_button.pack(pady=5)


#  LAUNCH GUI

root = tk.Tk()
app = LocatorApp(root)
root.mainloop()
WEATHER_DIR = app.weather_dir
OUTPUT_DIR = app.output_dir

print(WEATHER_DIR, OUTPUT_DIR)

def LOCMAKER(parent, child):
    return (parent + "/" + child)


def datecreator(strobj):
        strobj = str(strobj)
        y = int(strobj[0:4])
        m = int(strobj[4:6])
        d = int(strobj[6:8])
        dateobj = datetime.datetime(y,m,d)
        return dateobj


def dataaug(df):
    df = df[df.TAVG != -9999.0]
    df = df[df.WAVG != -9999.0]
    df = df[df.WMAX != -9999.0] 
    df['WAVG'] = df['WAVG'] / 10
    df['WMAX'] = df['WMAX'] / 10
    df['TAVG'] = df['TAVG'] / 10
    df['TMIN'] = df['TMIN'] / 10
    df['TMAX'] = df['TMAX'] / 10
    df['TRUEDATE'] = (df['DATE']).apply(datecreator)
    df['DATE'] = df['TRUEDATE'].apply(lambda x: x.toordinal())
    df['moving_temp'] = df['TAVG'].rolling(window = 5, center = True).mean()
    df['moving_wind'] = df['WAVG'].rolling(window = 5, center = True).mean()
    df['moving_rain'] = df['RMAX'].rolling(window = 5, center = True).mean()
    return df

def fluctuations(df):
    #wind
    wind = df[['TRUEDATE','DATE','WAVG', 'WMAX', 'moving_wind']]
    wind
    wind = wind.dropna()
    modelw = LinearRegression()
    modelw.fit(np.array(wind['DATE']).reshape((-1, 1)), np.array(wind['moving_wind']))
    slopew = modelw.coef_[0]
    cw = float(modelw.intercept_)
    wind['Wind_Linear_Model'] = (slopew * wind['DATE']) + cw
    windred = wind[['TRUEDATE', 'WMAX', 'moving_wind', 'Wind_Linear_Model']]
    windred.to_csv(f"{OVERALL_DIR}/RESULTS/windactmunich.csv")
    plt.plot(windred['TRUEDATE'], windred['WMAX'], color = 'green')
    plt.plot(windred['TRUEDATE'], windred['moving_wind'],color = 'yellow')
    plt.plot(windred['TRUEDATE'], windred['Wind_Linear_Model'], color = 'blue')
    plt.show()
    #temp
    temp = df[['TRUEDATE','DATE','TAVG', 'TMAX', 'TMIN','moving_temp']]
    temp = temp[temp.TMAX != -9999.0]
    temp = temp[temp.TMIN != -9999.0]
    temp['Dev_From_Avg_Gust'] = temp['TMAX'] - temp['TMIN']
    '''plt.fill_between(temp['TRUEDATE'], temp['TMIN'], temp['TMAX'], where=(temp['TMAX']> temp['TMIN']), interpolate = True,color='yellow')
    plt.plot(temp['TRUEDATE'], temp['moving_temp'])
    plt.show()'''
    temp = temp.dropna()
    modelt = LinearRegression()
    modelt.fit(np.array(temp['DATE']).reshape((-1, 1)), np.array(temp['moving_temp']))
    slopet = modelt.coef_[0]
    ct = float(modelt.intercept_)
    temp['Temp_Linear_Model'] = (slopet * temp['DATE']) + ct
    tempred = temp[['TRUEDATE', 'TMAX', 'TMIN', 'moving_temp', 'Temp_Linear_Model']]
    tempred.to_csv(f"{OVERALL_DIR}/RESULTS/tempactmunich.csv")
    plt.plot(tempred['TRUEDATE'], tempred['TMAX'], color = 'green')
    plt.plot(tempred['TRUEDATE'], tempred['moving_temp'],color = 'yellow')
    plt.plot(tempred['TRUEDATE'], tempred['Temp_Linear_Model'], color = 'blue')
    plt.show()
    #rain
    rain = df[['TRUEDATE', 'DATE', 'RMAX','moving_rain']]
    rain = rain[rain.RMAX != -9999.0]
    rain['Dev_From_Avg_Rain'] = rain['RMAX'] - rain['moving_rain']
    
    
    rain = rain.dropna()
    modelr = LinearRegression()
    modelr.fit(np.array(rain['DATE']).reshape((-1, 1)), np.array(rain['moving_rain']))
    sloper = modelr.coef_[0]
    cr = float(modelr.intercept_)
    rain['Rain_Linear_Model'] = (sloper * rain['DATE']) + cr
    rainred = rain[['TRUEDATE', 'RMAX', 'moving_rain', 'Rain_Linear_Model']]
    rainred.to_csv(f"{OVERALL_DIR}/RESULTS/rainactmunich.csv")
    plt.plot(rainred['TRUEDATE'], rainred['RMAX'], color = 'green')
    plt.plot(rainred['TRUEDATE'], rainred['moving_rain'],color = 'yellow')
    plt.plot(rainred['TRUEDATE'], rainred['Rain_Linear_Model'], color = 'blue')
    plt.show()
    return {'wind': slopew, 'temp':slopet, 'rain':sloper}


def dateextraction(df):
    DATELS = list(df['TRUEDATE'])
    md = list(set([d.strftime('%m-%d') for d in DATELS]))
    dates = {key: {} for key in md}
    df['MD'] = df['TRUEDATE'].apply(mdextraction)
    for k,v in dates.items():
        subdf = df[df['MD'] == k]
        modelr = LinearRegression()
        modelr.fit(np.array(subdf['DATE']).reshape((-1, 1)), np.array(subdf['moving_rain']))
        sloper = modelr.coef_[0]
        dates[k]['rc'] = float(modelr.intercept_)
        dates[k]['rm'] = sloper
        subdf['Rain_EXP'] = (dates[k]['rm'] * subdf['DATE']) + dates[k]['rc']
        modelt = LinearRegression()
        modelt.fit(np.array(subdf['DATE']).reshape((-1, 1)), np.array(subdf['moving_temp']))
        slopet = modelt.coef_[0]
        dates[k]['tc'] = float(modelt.intercept_)
        dates[k]['tm'] = slopet
        subdf['Temp_EXP'] = (dates[k]['tm'] * subdf['DATE']) + dates[k]['tc']
        modelw = LinearRegression()
        modelw.fit(np.array(subdf['DATE']).reshape((-1, 1)), np.array(subdf['moving_wind']))
        slopew = modelw.coef_[0]
        dates[k]['wc'] = float(modelw.intercept_)
        dates[k]['wm'] = slopew
        subdf['Wind_EXP'] = (dates[k]['wm'] * subdf['DATE']) + dates[k]['wc']
        subdf = subdf[['TRUEDATE', 'DATE', 'Rain_EXP', 'Temp_EXP', 'Wind_EXP']]
        dates[k]['df'] = subdf
    return dates
def mdextraction(dateobj):
    return dateobj.strftime('%m-%d')

def extremeweather(df, file):
    clean = df[df.WMAX != -9999.0]
    clean = clean[clean.TMAX != -9999.0]
    clean = clean[clean.TMIN != -9999.0]
    clean = clean[clean.RMAX != -9999.0]
    clean = clean.dropna()
    processed = dateextraction(clean)
    total = []
    for index, row in df.iterrows():
        orddate = row['DATE']
        mditem = mdextraction(row['TRUEDATE'])
        subdf = processed[mditem]['df']
        subdfrow = subdf.loc[subdf['DATE'] == orddate]
        if not subdfrow.empty:
            total.append(subdfrow)
    predicteddf = pd.concat(total, ignore_index=True)
    print(predicteddf)
    predrain = predicteddf[['TRUEDATE', 'Rain_EXP']]
    predrain.to_csv(f"{OVERALL_DIR}/RESULTS/rainpredmunich.csv")
    plt.plot(predicteddf['TRUEDATE'], predicteddf['Rain_EXP'])
    plt.show()
    predtemp = predicteddf[['TRUEDATE', 'Temp_EXP']]
    predtemp.to_csv(f"{OVERALL_DIR}/RESULTS/raintempmunich.csv")
    plt.plot(predicteddf['TRUEDATE'], predicteddf['Temp_EXP'])
    plt.show()
    predwind = predicteddf[['TRUEDATE', 'Wind_EXP']]
    predwind.to_csv(f"{OVERALL_DIR}/RESULTS/windpredmunich.csv")
    plt.plot(predicteddf['TRUEDATE'], predicteddf['Wind_EXP'])
    plt.show()
    yearcount = {}
    for index, row in df.iterrows():
        date = row['DATE']
        actualdate = row['TRUEDATE']
        year = int(actualdate.year)
        if year not in yearcount.keys():
            yearcount[year] = 0
        predrow = predicteddf.loc[predicteddf['DATE'] == date]
        if not predrow.empty:
            if row['RMAX'] >= 1.7* (predrow['Rain_EXP'].iloc[0]):
                #print("Extreme Rain")
                yearcount[year] += 1 
            elif row['TMAX'] >= (9 +(predrow['Temp_EXP'].iloc[0])) or row['TMIN'] <= ((predrow['Temp_EXP'].iloc[0])-9):
                #print("Extreme Temp")
                yearcount[year] += 1 
            elif row['WMAX'] >= 24.5:
                #print("Extreme Wind")
                yearcount[year] += 1 
            else:
                continue
    yearcount.pop(2025)
    rowls = []
    for k,v in yearcount.items():
        row = {'Year': k, 'Extreme Days': v}
        rowls.append(row)
    extremes = pd.DataFrame.from_dict(rowls)
    
    a, b = np.polyfit(extremes['Year'], extremes['Extreme Days'], 1)
    extremes['model'] = (a * extremes['Year']) + b
    plt.plot(extremes['Year'], extremes['Extreme Days'])
    plt.plot(extremes['Year'], extremes['model'])
    plt.show()
    extremes.to_csv(f"{OVERALL_DIR}/RESULTS/{file}")




def processorfunc(file):
    name = file
    print(name.rstrip('_.csv'))
    dfls = []
    for v in VARS:
        col = VARDICT[v]
        vfolder = LOCMAKER(OVERALL_DIR, v)
        specific = LOCMAKER(vfolder, name)
        df = pd.read_csv(specific)
        df = df[['DATE',col]]
        if v == 'max_temp':
            df.columns = ['DATE', 'TMAX']
        elif v == 'min_temp':
            df.columns = ['DATE', 'TMIN']
        elif v == 'max_wind':
            df.columns = ['DATE', 'WMAX']
        elif v == 'mean_temp':
            df.columns = ['DATE', 'TAVG']
        elif v == 'mean_wind':
            df.columns = ['DATE', 'WAVG']
        else:
            df.columns = ['DATE', 'RMAX']
        dfls.append(df)
    overalldf = dfls[0]
    for index, df in enumerate(dfls):
        if index < len(VARS) -1:
            overalldf = pd.merge(overalldf, dfls[index + 1],on ='DATE', how='outer')
    clean = overalldf.dropna()
    augmented = dataaug(clean)
    coefs = fluctuations(augmented)
    extremeweather(augmented,file)


# Find locations with complete data across all variables.
netdict = {}
for v in VARS:
    vfolder = LOCMAKER(OVERALL_DIR, v)
    vfiles = [f for f in os.listdir(vfolder) if f.endswith(('.csv'))]
    for vf in vfiles:
        if vf in netdict.keys():
            netdict[vf].append(v)
        else:
            netdict[vf] = [v]
completes = []

for k,v in netdict.items():
    if len(v) == 6:
        completes.append(k)
print(completes)
# Create joint dataframe per location

VARDICT = {'max_temp':'TX', 'min_temp': 'TX', 'max_wind':'FX', 'mean_temp':'TX', 'mean_wind':'FG', 'rain':'RR'}

processorfunc('52_DE_MUENCHEN_.csv')