# DataCompare 
(name wip)\
This is a Python-based desktop application with a primary focus on making comparing datasets and performing minor transformations quicker and easier for the average user. I am primarily just doing this for fun and to learn and challenge myself.

## Goal
This tool is designed to make **data validation and comparison** accessible to anyone who works with spreadsheets or tabular data (analysts, QA testers, or engineers) without needing to write scripts in pandas, Excel, or SQL.

Future versions aim to include:
- More **transformation tools** (filtering, normalization, and column mapping)
- Support for **larger datasets** (via Polars or DuckDB)
- **Custom merge rules** and visual diffing between datasets

## Features
(Some features have yet to be added)
- Load datasets in multiple formats:
  - CSV, TSV, and TXT files  
  - Excel files (.xls, .xlsx, .xlsm, .xlsb, .ods)  
  - JSON, Parquet, Feather, HTML, Stata, SAS, and Pickle files  
- Compare columns and identify matching and non-matching records  
- Perform joins and merges directly through the user interface
- Modify values based on user parameters (ex: Change values in Column B if Column A Values > 10)
- Clean NULLs (Delete NULL records to set them to a specific value)
- Export results to a new file  
- Built-in data preview with sorting and resizing support  
- Works locally with no network connection required


## How it works
- **Load Files** -- Select or drag/drop a file into any of the two data panels that are labelled with A or B
- **Preview Data** -- Each file's top 10 rows will be displayed for review
- **Select Columns** -- Choose the columns to match or merge on
- **Compare or Merge** -- The center panel will update with the selected operation's results
- **Export** -- Save your changes to a new file
