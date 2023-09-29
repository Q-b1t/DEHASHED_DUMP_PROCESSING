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
## Examples:
```
python .\dehashed_dump_processing.py -c .\conf_test.cfg -d awesome_enterprise.eu -o leaks_a -f csv -v True
```

```
python .\dehashed_dump_processing.py -d awesome_enterprise.eu -o credenciales
```

```
python .\dehashed_dump_processing.py -d awesome_enterprise.eu -f csv -s 20000 -p 2
```

```
python .\dehashed_dump_processing.py -d awesome_enterprise.eu -f csv -n null
```