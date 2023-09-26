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
    parser.add_argument("-o","--output_file",help="Name of excel book the data will be exported to (default: \"dehashed_dump.xlsx\")",type=str,default="dehashed_dump.xlsx",nargs="?")
    parser.add_argument("-n","--null_value",help="Specify a different null value to fill the blank spaces (default: np.nan)",type=str,default=np.nan,nargs="?")
    parser.add_argument("-g","--insights",help="Whether to generate graphs used in reports (default: np.nan)",type=bool,default=False,nargs="?")
    parser.add_argument("-c","--config_file",help="Configuration file contianing the API keys (default: \"conf.cfg\")",type=str,default="conf.cfg",nargs="?")
    parser.add_argument("-s","--size",help="The number of requests to be made in the Dehashed API (view API documentation)",type=int,default=1000,nargs="?")
    parser.add_argument("-p","--pages",help="Configuration file contianing the API keys (default: \"conf.cfg\")",type=int,default=1,nargs="?")
    parser.add_argument("-d","--domain",help="The mail domain to make searches on (default: \"dehashed.com\")",type=str,default="dehashed.com",nargs="?")


    # retrieve cli arguments
    args: Namespace = parser.parse_args()
    export_file = args.output_file
    config_file = args.config_file
    na_value = args.null_value
    insights = args.insights
    size = args.size 
    pages = args.pages
    domain = args.domain

    # get configuration values
    config = configparser.ConfigParser()
    config.read(config_file)
    assert config['API_KEY']['dehashed'] != "" or config['API_KEY']['email'] != "", colored("[-] The configuration file does not contain an API key, email or the format is not the appropiate one.","red")

    DEHASHED_API_KEY = config['API_KEY']['dehashed']
    VERIFICATION_MAIL = config['API_KEY']['email']

    response = make_dehashed_request(mail=VERIFICATION_MAIL,api_key=DEHASHED_API_KEY,num_requests=size,num_pages=pages,domain=domain)
    if response.status_code == 200:
        json_data = json.loads(response.text)
    else:
        print(colored("Response was not successful","red"))
        sys.exit()

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
        # if true, generate the insights
        generate_insights(parsed_table=parsed_table)
    else:
        print(colored(f"[-] The dump was not successful","red"))
    

    
    