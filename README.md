# Climate Modelling Data Preparation
<img width="652" height="93" alt="image" src="https://github.com/user-attachments/assets/bc9d535c-0ff2-4ede-962e-772eeb9ae526" />


Please note that the following instructions and scripts were produced externally to ECAD, this is unofficial software designed for improving the ease of use for my fellow researchers using ECAD datasets.

# File processor and data preparation for machine-learning model-building on European Climate data from ECAD. 

Pre-requisites: Python or Conda is installed on your machine. The following tutorial is for windows devices.

1) Download this repository as a zip folder and then extract all to your chosen directory. Alternatively, if you have git installed, you can clone via: 
git clone https://github.com/icprofsensei/Climate_Modelling_Data_Preparation.git

2) Open the command prompt and navigate to your directory.
**cd [YOUR PROJECT DIRECTORY]**

3) Create a virtual environment for your repository:
**python -m venv env**

4) Activate your virtual environment:
**env\Scripts\activate.bat**

5) Install all the required packages:
**(env) pip install -r requirements.txt**

6) Download the desired zip files for European Climate data:
Visit the link here: https://www.ecad.eu/dailydata/predefinedseries.php

7) Extract the climate files from your zip folder to another repository. I would recommend the following directory structure:
>[YOUR PROJECT DIRECTORY]
>>env

>>database (Location where your database will be created)


>>data (Extract zip folder here)


>>All files in my repository: csv_processor.py, folder_parser.py ...

8) In the command prompt, launch the file processor and follow the instructions to open the folder of unzipped climate .txt files, specify the desired destination where your results folder should be created (I recommend 'data' as above) and select the variable under investigation from the radio buttons :
**python -m folder_parser**

9) A loading bar should be displayed as the script runs - it will create a folder of .parquet files. Do this for all the variables and folders of interest.

10) Once complete, you will now load the .parquet files into a duck database. For each variable of interest, select the corresponding folder of .parquet files and specify a location (I recommend 'database' as above).

**python -m mlpreproc**

11) Another loading bar should be displayed as the script runs. Once complete, a summary table showing the different variations on the target variable will be displayed.

12) To view a summary of acceptable files for one particular target variable, you can run the command:

**python -m processor**

This will prompt you to highlight the target variable, database and variation number. 

13) You can run custom SQL queries on your database and then specify the output - either a printed output (of the first 30 lines in the dataframe), a .csv, or a .parquet file.

**python -m SQL_query_tool**

14) If you produce a custom .csv file, you can extract basic insights and complete basic data cleaning. 
    
**python -m csv_processor**

15) This will create a results folder displaying (a) Raw line chart (b) 10 day moving average line chart (c) 30 day moving average line chart (d) Linear model coefficients density diagram for each day of the year (e) Linear model line chart for each day of the year (f) Cleaned csv files for further processing.


**Please note the following advice for referencing ECAD datasets for research papers or publications of your own:**

a) For **ECA&D**:
“We acknowledge the data providers in the ECA&D project.
Klein Tank, A.M.G. and Coauthors, 2002. Daily dataset of 20th-century surface air
temperature and precipitation series for the European Climate Assessment. Int. J. of Climatol.,
22, 1441-1453.
Data and metadata available at https://www.ecad.eu”


b) For **E-OBS**:
“We acknowledge the E-OBS dataset and the data providers in the ECA&D project
(https://www.ecad.eu).
Cornes, R., G. van der Schrier, E.J.M. van den Besselaar, and P.D. Jones. 2018: An Ensemble
Version of the E-OBS Temperature and Precipitation Datasets, J. Geophys. Res. Atmos., 123.
doi:10.1029/2017JD028200"
