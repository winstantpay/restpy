import config
import requests
import json
from typing import Dict, List
from pprint import pprint

TOKEN:str = ''
CLIENT_ID: int = 0


def login() -> str:
    global TOKEN
    base_url: str = 'http://doc.worldkyc.com/client/auth/'
    auth_record: json =  { "username": config.userLogin, "password": config.userPassword  }
    result= requests.post(base_url, data=auth_record).json()
    TOKEN = result["token"]

    # result= requests.post(base_url, data=auth_record)
    # print(json.dumps(auth_record, indent=2, sort_keys=True))
    # print(result.text)
    #
    # exit(-1)

    return TOKEN

#
# The readData fundtion reads the client data
#
def readData(client: int) -> json:

    with open('./data/clients.json') as f:
        data: json = json.load(f)

    return data[client]

#
# The registerClient function
#
def registerClient(requirement_id: int, requirements: json ,client: json) -> json:

    global CLIENT_ID
    global TOKEN

    base_url: str = 'http://doc.worldkyc.com/client/signup/'
    APIkey:str  = config.APIKey
    TOKEN =  login()
    url: str = "{0}?service_caller_id={1}".format(base_url, APIkey)

    if(requirement_id>0):
        url = "{0}&requirement_id={1}".format(url, requirement_id)

    if CLIENT_ID > 0:
        url = "{0}&client_id={1}".format(url, CLIENT_ID)

    print(url)

    nc: json = {}

    for elem in requirements["fields"]:
        key:str =elem["name"]
        value: str = client[key]
        nc[key] = value

    print(json.dumps(nc, indent=2, sort_keys=True))
    trx_header = {'Authorization': 'token {}'.format(TOKEN)}
    result = requests.post(url, headers = trx_header, data=nc).json()

    print(json.dumps(result, indent=2, sort_keys=True))

    if ('id' in result):
        CLIENT_ID = result["id"]
        print('Set Client Id {}'.format(CLIENT_ID))

    return result

#
# The HandleStep fundtion
#
def handleStep(requirements_id: int, requirements: json ,url: str ) -> int:

    client: json = readData(0)

    newKYCClient:json = registerClient(requirements_id, requirements, client)

    next_id = requirements["requirement_id"] # This field holds the next requirement

    return next_id

#
# The nain
#
def main():
    base_url: str = 'http://doc.worldkyc.com/client/schema/'
    APIkey:str  = config.APIKey

    TOKEN =  login()

    url: str = base_url + '?service_caller_id=' + APIkey
    result: json = requests.get(url).json()
    next_id: int  =  handleStep(0, result,url)

    while next_id != None:
        url = base_url + '?service_caller_id=' + APIkey + '&requirement_id={}'.format(next_id)
        result = requests.get(url).json()
        next_id = handleStep(next_id,result,url)


#
# Invoke Main from here to solve accidential import
#
if __name__ == "__main__":
    main()