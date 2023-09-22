import json
import numpy as np
import pandas as pd
from termcolor import colored
from argparse import ArgumentParser,Namespace

def read_data(dump_file):
    """
    Inputs:
        - dump_file: Path of the file containing the json dump.
    Outputs:
        - json_data: json object
    """
    with open(dump_file,"r",encoding="utf-8") as f:
        json_data = f.readlines()
    f.close()
    return json_data[0]

def parse_data(entries,na_value):
    """
    Inputs: 
        - entries: A list of dictionaries containing one breached sample each. The keys will be used as columns to parse the data 
        into an ordered table.
    Outputs:
        - parsed_table: Returns a parsed Dataframe with all the entries. The missing values are replaced with numpy's default missing value.
    """
    print(colored("[*] Parsing entries...","blue"))
    entries_series = [pd.Series(entry) for entry in entries]
    parsed_table = pd.DataFrame(entries_series)
    parsed_table.replace(r'^\s*$', np.nan, regex=True,inplace=True)
    parsed_table.fillna(na_value,inplace=True)
    filtered_table = parsed_table[ (parsed_table["password"] != na_value) | (parsed_table["hashed_password"] != na_value) ]

    print(colored(filtered_table.head(),"blue"))
    return filtered_table

def save_table(parsed_table,save_path):
    """
    Inputs: 
        - parsed_table: A processed pandas dataframe.
        - save_path: The to which the table will be saved as an excel book.
    """
    parsed_table.to_excel(save_path, index=False)
    print(colored(f"[+] Breached data saved to {save_path}","green"))



if __name__ == '__main__':
    # instance command line parser
    parser = ArgumentParser()
    parser.add_argument("-i","--input_file",help="Name json file dumped using the DEHASHED API (default: \"breached_passwords.json\")",type=str,default="breached_passwords.json",nargs="?")
    parser.add_argument("-o","--output_file",help="Name of excel book the data will be exported to (default: \"dehashed_dump.xlsx\")",type=str,default="dehashed_dump.xlsx",nargs="?")
    parser.add_argument("-n","--null_value",help="Specify a different null value to fill the blank spaces (default: np.nan)",type=str,default=np.nan,nargs="?")

    args: Namespace = parser.parse_args()
    dump_file = args.input_file
    export_file = args.output_file
    na_value = args.null_value

    
    # load the json data as a python dictionary
    json_data = json.loads(read_data(dump_file=dump_file))

    # extract usefull metadata from the dump
    num_entries = json_data["total"]
    dump_status = json_data["success"]
    entries = json_data["entries"]
    if dump_status:
        print(colored(f"[+] The fetch was successful. {num_entries} potential breached credentials found.","green"))
        # parse the data into an ordered table
        parsed_table = parse_data(entries=entries,na_value=na_value)
        # save the data to excel
        save_table(parsed_table=parsed_table,save_path=export_file)
    else:
        print(colored(f"[-] The dump was not successful","red"))
    

    
    