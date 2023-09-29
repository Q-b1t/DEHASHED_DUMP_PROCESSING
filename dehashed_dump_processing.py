import json
import numpy as np
import pandas as pd
from termcolor import colored
from argparse import ArgumentParser,Namespace
import os
import matplotlib.pyplot as plt
import requests
import configparser
import sys
import re

def validate_name(output_name,output_format):
    pattern = r"[A-Za-z0-9-_]{3,20}"
    assert re.match(pattern,output_name) and "." not in output_name ,colored(f"[-] {output_name} name is not valid. Please limit to numbers, lower and upper case letters, and special characters: \"-\",\"_\". Please do not include the file extention.","red")
    assert output_format == "excel" or  output_format == "csv", colored("[-] Output format must be either \"excel\" or \"csv\".","red")


def make_dehashed_request(mail,api_key,num_pages,num_requests,domain):
    headers = {
        'Accept': 'application/json',
    }
    response = requests.get(
        f'https://api.dehashed.com/search?query=domain:{domain}&size={num_requests}&page={num_pages}',
        headers=headers,
        auth=(mail, api_key),
    )
    return response


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

def parse_data(entries,na_value,verbose):
    """
    Inputs: 
        - entries: A list of dictionaries containing one breached sample each. The keys will be used as columns to parse the data 
        into an ordered table.
    Outputs:
        - parsed_table: Returns a parsed Dataframe with all the entries. The missing values are replaced with numpy's default missing value.
    """
    if verbose:
        print(colored("[*] Parsing entries...","blue"))
    entries_series = [pd.Series(entry) for entry in entries]
    parsed_table = pd.DataFrame(entries_series)
    parsed_table.replace(r'^\s*$', np.nan, regex=True,inplace=True)
    parsed_table.fillna(na_value,inplace=True)
    filtered_table = parsed_table[ (parsed_table["password"] != na_value) | (parsed_table["hashed_password"] != na_value) ]
    if verbose:
        print(colored(filtered_table.head(),"blue"))
    return filtered_table

def save_table(parsed_table,save_path,output_format,verbose):
    """
    Inputs: 
        - parsed_table: A processed pandas dataframe.
        - save_path: The to which the table will be saved as an excel book.
    """
    if output_format == "csv":
        filename = save_path + "." + "csv"
        parsed_table.to_csv(filename,index = False)
    else:
        filename = save_path + "." + "xlsx"
        parsed_table.to_excel(filename, index=False)
         
    if verbose:
        print(colored(f"[+] Breached data saved to {filename}","green"))

def generate_insights(parsed_table):
    """
    Generates graphs that are useful for reporting purposes
    Inputs:
        - parsed_table: A processed pandas dataframe.
    """
    # bar graph of all leaks and databases
    database_counts = parsed_table["database_name"].value_counts()
    n_bars = 15 if len(database_counts) >= 15 else len(database_counts)
    database_counts = database_counts.nlargest(n = n_bars)

    plt.figure(figsize=(15,10))
    plt.barh(database_counts.keys(),database_counts.values)
    plt.yticks(rotation=45,fontsize=10)
    plt.title(f"Top {n_bars} leak databanks with most credentials related to the company.")
    plt.savefig("leak_databases.png")

if __name__ == '__main__':
    # instance command line parser
    parser = ArgumentParser()
    parser.add_argument("-o","--output_file",help="Name of excel book the data will be exported to (default: \"dehashed_dump\")",type=str,default="dehashed_dump",nargs="?")
    parser.add_argument("-n","--null_value",help="Specify a different null value to fill the blank spaces (default: np.nan)",type=str,default=np.nan,nargs="?")
    parser.add_argument("-c","--config_file",help="Configuration file contianing the API keys (default: \"conf.cfg\")",type=str,default="conf.cfg",nargs="?")
    parser.add_argument("-s","--size",help="The number of requests to be made in the Dehashed API (view API documentation)",type=int,default=1000,nargs="?")
    parser.add_argument("-p","--pages",help="Configuration file contianing the API keys (default: \"conf.cfg\")",type=int,default=1,nargs="?")
    parser.add_argument("-d","--domain",help="The mail domain to make searches on (default: \"dehashed.com\")",type=str,default="dehashed.com",nargs="?")
    parser.add_argument("-v","--verbose",help="Whether to output information on the script's progress in the console",type=bool,default=False,nargs="?")
    parser.add_argument("-f","--output_format",help="It can be either \"excel\" or \"csv\" (default: \"excel\")",type=str,default="excel",nargs="?")


    # retrieve cli arguments
    args: Namespace = parser.parse_args()
    export_file = args.output_file
    config_file = args.config_file
    na_value = args.null_value
    size = args.size 
    pages = args.pages
    domain = args.domain
    verbose = args.verbose
    output_format = args.output_format


    validate_name(output_name=export_file,output_format=output_format)

    # get configuration values
    config = configparser.ConfigParser()
    config.read(config_file)
    assert config['API_KEY']['dehashed'] != "" or config['API_KEY']['email'] != "", colored("[-] The configuration file does not contain an API key, email or the format is not the appropiate one.","red")

    DEHASHED_API_KEY = config['API_KEY']['dehashed']
    VERIFICATION_MAIL = config['API_KEY']['email']
    if verbose:
        print(colored(f"[+] The api key has been succesfully retrieved.\nQuering domains...","green"))

    # make api request
    response = make_dehashed_request(mail=VERIFICATION_MAIL,api_key=DEHASHED_API_KEY,num_requests=size,num_pages=pages,domain=domain)
    
    # parse the response
    json_data = json.loads(response.text)

    if response.status_code == 200:
        # extract usefull metadata from the dump
        num_entries = json_data["total"]
        dump_status = json_data["success"]
        entries = json_data["entries"]
        if dump_status and entries is not None:
            if verbose:
                print(colored(f"[+] The fetch was successful. {num_entries} potential breached credentials found.","green"))
            # parse the data into an ordered table
            parsed_table = parse_data(entries=entries,na_value=na_value,verbose = verbose)
            # save the data to excel
            save_table(parsed_table=parsed_table,save_path=export_file,output_format= output_format,verbose = verbose)
        else:
            print(colored(f"[-] The dump was not successful. Perhaps it could be the domain. Please verify your inputs.","red"))
    else:
        message = json_data["message"]
        print(colored(f"Query was not successful.\nResponse code: {response.status_code}\n{message}","red"))
        sys.exit()


    

    
    