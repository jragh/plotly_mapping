# Project Readme
## Instructions on Running the current project

In order to run the current project, you will need to download the base files which contain the CMA boundaries and attribution. I have already cleaned the data to include the travel to work attribution as part of the geojson from the initial census file.

**Files to Download**
 - census_2021_shapes.geojson
 - CTTravelByMode.csv

Once this file is downloaded, you will need to run the data cleaning step. This will call functions from other files included in the project which will do the following:

 - Take the travel to work attribution from the CSV and assign it to the boundaries JSON
 - Convert JSON to GeoJSON (Already done, this is done by writing as GeoJSON)
 - Reduce the accuracy of the GeoJSON polygon boundaries to save space
 - generate the aggregate stats for each of the CMAs / CAs
 - Save all output files in same directory

**Run Data Cleaning Step**

 - Navigate to root folder which contains both app.py and data_cleaning.py  
 - Run the following command in your command terminal: `python3 -m data_cleaning`

**Launch App**

- Run the following command in your terminal (or whichever command you use to run your app): `python3 -m app`