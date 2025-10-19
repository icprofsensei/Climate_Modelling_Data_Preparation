import duckdb as ddb
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from summarise import PROCESS

class LocatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title('File Selector')
        self.root.geometry("800x500")
        self.db = ""
        self.var_num_value = 0
        self.selection = ""
        self.create_widgets()

    def select_db_file(self):
        self.db = filedialog.askopenfilename(title = "Select the database file: ")
        if self.db:
            self.db_file.delete(0, tk.END)
            self.db_file.insert(0, self.db)
    
    def submit(self):
        var_num_text = self.var_num_entry.get()
        selection_val = self.selection.get()
        
        if not self.db or not var_num_text or not selection_val:
            messagebox.showwarning("Input Error: Complete all fields")
        else:
            self.var_num_value = int(var_num_text)
            self.selection = selection_val
            try:
                self.root.destroy()
            except Exception as e:
                messagebox.showerror(f"Error {e} occurred")
    
    def val(self, text):
        if text == "":
            return True
        try:
            float(text)
            return True
        except:
            return False
    
    def create_widgets(self):
        inputlab = tk.Label(self.root, text= "Database Location:")
        inputlab.grid(row=0, column = 1)
        self.db_file = tk.Entry(self.root, width = 50)
        self.db_file.grid(row=1, column = 1)
        inputbutton = tk.Button(self.root, text = "Browse", command = self.select_db_file)
        inputbutton.grid(row=2, column = 1, pady=5)

        varnumlab = tk.Label(self.root, text= "Variable Number: ")
        varnumlab.grid(row=3, column = 1, pady=5)
        vcmd = (self.root.register(self.val), '%P')
        self.var_num_entry = tk.Entry(self.root, width=50, validate="key", validatecommand=vcmd)
        self.var_num_entry.grid(row=4, column = 1, pady=5)

        figtype = tk.Label(self.root, text = "What variable is being investigated?")
        figtype.grid(row=5, column = 1, pady=5)
        self.selection = tk.StringVar(value = "Image")
        frame = tk.Frame(self.root)#
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
        submit_button.grid(row=12, column = 2,pady=5)

root = tk.Tk()
app = LocatorApp(root)
root.mainloop()


varnum = app.var_num_value
duckdb_path = app.db
var = app.selection
feature_dict = {
    'DailyMaximumTemperature': 'TX',
    'DailyMinimumTemperature': 'TN',
    'DailyMeanTemperature': 'TG',
    "DailyPrecipitationAmount":'RR',
    "DailyMeanSeaLevelPressure":'PP',
    "DailyCloudCover":'CC',
    "DailyHumidity":'HU',
    "DailySnowDepth":'SD',
    "DailySunshineDuration":'SS',
    "GlobalRadiation":'QQ',
    "DailyMeanWindSpeed":'FG',
    "DailyMaximumWindGust":'FX',
    "DailyWindDirection":'DD'
}  

PROCESS(app.db, var, feature_dict[var], varnum).consistent()