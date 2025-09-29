# Climate Modelling Data Preparation
File processor and data preparation for machine-learning model-building on European Climate data from ECAD. 

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


>>data (Extract zip folder here)


>>All files in my repository: csv_processor.py, folder_parser.py ...

8) In the command prompt, launch the file processor and follow the instructions to open the folder of unzipped climate files and the desired destination where your results folder should be created (I recommend 'data' as above):
**python -m folder_parser**

9) A loading bar should be displayed as the script runs.

10) To extract basic insights and complete basic data cleaning on a specific file run:
**python -m csv_processor.py**

11) This will create a results folder displaying (a) Raw line chart (b) 10 day moving average line chart (c) 30 day moving average line chart (d) Linear model coefficients density diagram for each day of the year (e) Linear model line chart for each day of the year (f) Cleaned csv files for further processing.

