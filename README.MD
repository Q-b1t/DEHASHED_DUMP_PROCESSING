# Dehashed Dump Processing
This python script was made in the intent to parse breached data obtained via the [DEHASHED](https://www.dehashed.com) API. 
It takes the dump json file obtained from DEHASHED, parses it into an ordered table, fills the missing values with "NAN", and exports it to an excel book format.
# Usage:
In order to install the necesary dependencies run:
```
pip install -r requirements.txt
``` 
In order to run the script run:
```
python3 dehashed_dump_processing.py
```
Finally, it is possible to change the default input and output file names from the command line. You can type the following command to see the required inputs to overwrite them:
```
python3 dehashed_dump_processing.py --help
```
#### Default values:
- json dump: ```breached_passwords.json```
- excel output file: ```dehashed_dump.xlsx```
