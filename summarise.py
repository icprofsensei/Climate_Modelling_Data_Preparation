import duckdb as ddb
import datetime

currentDateTime = datetime.datetime.now()
date = currentDateTime.date()
year = date.strftime("%Y")
class FIELDS():
    def __init__(self, duckdb_path, featurename):
        self.duckdb_path = duckdb_path
        self.featurename = featurename
    def show(self):
        con = ddb.connect(database=self.duckdb_path, read_only=False)
        elements = con.sql(f"""SELECT *
                           FROM 
                           {self.featurename}_elements ELE
                           """)
        print(elements)

        
class PROCESS():
    def __init__(self, duckdb_path, feature, featurename, varnum):
        self.duckdb_path = duckdb_path
        self.feature = feature
        self.featurename = featurename
        self.varnum = varnum
    def consistent(self):
        con = ddb.connect(database=self.duckdb_path, read_only=False)
        elements = con.sql(f"""SELECT SOU.STAID, SOU.SOUID, SOU.SOUNAME, SOU.CN, SOU.LAT, SOU.HGHT, SOU.START, SOU.STOP, STA.STANAME
                           FROM {self.featurename}_sources SOU
                           INNER JOIN 
                           {self.featurename}_elements ELE
                           ON SOU.ELEI=ELE.ELEID
                           LEFT JOIN 
                           {self.featurename}_stations STA
                           ON SOU.STAID = STA.STAID 
                           WHERE SOU.ELEI = '{self.feature}{self.varnum}'
                           AND date_part('year',SOU.STOP) = {year}
                           """)
        print(elements)
