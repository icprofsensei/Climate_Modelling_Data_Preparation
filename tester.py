import duckdb
location = "C:/Users/Dhyla/Documents/Startup_success/climastock4/weather.db"
con = duckdb.connect(location)
con.sql("SELECT * FROM HUMIDITY limit 10").show()