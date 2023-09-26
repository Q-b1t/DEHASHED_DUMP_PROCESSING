# Dehashed Dump Processing
This python script was made in the intent to parse breached data obtained via the [DEHASHED](https://www.dehashed.com) API. 
It makes a request to the API in cuestion and parses the data into an excel book if the response is successfull.
# Usage:
## Installing dependencies
In order to install the necesary dependencies run:
```
pip install -r requirements.txt
``` 
It is recommended to run the script inside a python virtual environment.
## Set up the configuration file
In the root directory of the project, a file named ```conf.cfg``` can be found. For the script to run, it is necessary to set up such file with the corresponding values accordingly. 
### Example:
```
[API_KEY]
dehashed = s4i0e2358fkgw9c
email = my_mail@gmail.com
``` 
The values to fill are a Dehashed API key and the mail to which the key is associated with.

## Run the script
In order to run the script run:
```
python3 dehashed_dump_processing.py
```
Finally, the script emulates a CLI. Therefore, some parameters can be changed using the appropriate tags. To see the available options run:
```
python3 dehashed_dump_processing.py --help
```

#### Tags
- --null_value: This tag can be set up in order to fill the table's empty values with a certain value.
- --insights: This flag can be set to ```True``` in order to generate a graph to use in reports.
- --config_file: This flag can be set to change the default configuration file (```conf.cfg```).
- --size: This flag can set to change the number of requests to make (View [Dehashed API's documentation](https://www.dehashed.com/docs) for more details).
- -- pages: This flag can be set to limit the pages to display the information (View [Dehashed API's documentation](https://www.dehashed.com/docs) for more details).
- --domain: This flag **needs to be set up to specify the domain you want to search for**.
