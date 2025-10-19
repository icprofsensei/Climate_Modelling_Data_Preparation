import duckdb as ddb
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from summarise import PROCESS
import polars as pl
import datetime

class QueryApp:
    def __init__(self, root):
        self.root = root
        self.root.title('SQL QUERY')
        self.root.geometry("500x700")
        self.db = ""
        self.output_dir = ""
        self.query = """-"""
        self.selection = ""
        self.create_widgets()

    def select_db_file(self):
        self.db = filedialog.askopenfilename(title = "Select the database file: ")
        if self.db:
            self.db_file.delete(0, tk.END)
            self.db_file.insert(0, self.db)
    def select_output_dir(self):
        self.output_dir = filedialog.askdirectory(title = "Select the folder where the output files will be created: ")
        if self.output_dir:
            self.outputloc.delete(0, tk.END)
            self.outputloc.insert(0, self.output_dir)
    

    def submit(self):
        query_val = self.queryentry.get("1.0", tk.END).strip()
        selection_val = self.selection
        if not query_val or not self.db or not selection_val:
            messagebox.showwarning("Input Error"," Provide a database, a query and an output format")
        else:
            self.query = query_val
            self.selection = selection_val
            if self.selection in ['CSV', 'PARQUET'] and self.output_dir == '':
                    messagebox.showwarning("Input Error"," Complete all fields")
            else:
                try:
                    self.run_query()
                except Exception as e:
                    messagebox.showerror("Error", f"Error {e}")
    
    def create_widgets(self):
        inputlab = tk.Label(self.root, text= "Database Location:")
        inputlab.pack(pady=5)
        self.db_file = tk.Entry(self.root, width = 50)
        self.db_file.pack(pady=5)
        inputbutton = tk.Button(self.root, text = "Browse", command = self.select_db_file)
        inputbutton.pack(pady=5)


        outputlab = tk.Label(self.root, text= "Output directory")
        outputlab.pack(pady=5)
        self.outputloc = tk.Entry(self.root, width = 50)
        self.outputloc.pack(pady=5)
        outputbutton = tk.Button(self.root, text = "Browse", command = self.select_output_dir)
        outputbutton.pack(pady=5)


        querytext = tk.Label(self.root, text= "SQL Query: ")
        querytext.pack(pady=5)
        self.queryentry = tk.Text(self.root, width=50, height = 10)
        self.queryentry.pack(pady=5)

        figtype = tk.Label(self.root, text = "Result Output:")
        figtype.pack(pady=5)
        self.selection = tk.StringVar(value = "Image")
        frame = tk.Frame(self.root)
        frame.pack(pady=5)
        CSV = tk.Radiobutton(self.root, text="CSV", variable=self.selection, value="CSV")
        PARQUET= tk.Radiobutton(self.root, text="PARQUET", variable=self.selection, value="PARQUET")
        PRINT = tk.Radiobutton(self.root, text="PRINT", variable=self.selection, value="PRINT")
        CSV.pack(pady=5)
        PARQUET.pack(pady=5)
        PRINT.pack(pady=5)
        submit_button = tk.Button(self.root, text = "Submit", command = self.submit)
        submit_button.pack(pady=5)
    
    def run_query(self):
        print(self.query)
        timestamp = str(datetime.datetime.now())
        timestamp = "".join([t for t in timestamp if t not in [' ', '.', ',', '/', '-', ':']])
        con = ddb.connect(self.db)
        result = con.execute(self.query).pl().lazy()
        if self.selection == 'PRINT':
            print("Loading Preview")
            result_preview = result.head(30).collect()
            print(result_preview)
            print("Finished")
            con.close()
        elif self.selection == 'CSV':
            print("Loading Result to CSV")
            result.collect().write_csv(self.output_dir + '/results' + timestamp + '.csv', separator=",")
            print("Finished")
            con.close()
        else:
            print("Loading Result to PARQUET")
            result.collect().write_parquet(
                self.output_dir + '/results' + timestamp + '.parquet',
                use_pyarrow=True,
            )
            print("Finished")
            con.close()
root = tk.Tk()
app = QueryApp(root)
root.mainloop()
