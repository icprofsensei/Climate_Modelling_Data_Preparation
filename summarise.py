import duckdb as ddb
import datetime

currentDateTime = datetime.datetime.now()
date = currentDateTime.date()
year = date.strftime("%Y")
class FIELDS():
    def __init__(self, duckdb_path, feature, featurename):
        self.duckdb_path = duckdb_path
        self.feature = feature
        self.featurename = featurename
    def show(self):
        con = ddb.connect(database=self.duckdb_path, read_only=False)
        elements = con.sql(f"""SELECT *
                           FROM 
                           {self.featurename}_elements ELE
                           """)
        print(elements)
    
