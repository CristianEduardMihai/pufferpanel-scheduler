import requests
import yaml
import os
import time
import datetime

with open("config.yaml", "r") as config_yaml:
    try:
        configdata = yaml.safe_load(config_yaml)
    except yaml.YAMLError as exc:
        print(exc)

#set the timezone
os.environ['TZ'] = configdata["timezone"]
time.tzset()

client_id = configdata["client_id"]
client_secret = configdata["client_secret"]
server_ip_port = "http://" + configdata["server_ip_port"]

#get the 0auth token
raw_token = requests.post(server_ip_port + "/oauth2/token", headers={"Content-Type":"application/x-www-form-urlencoded"}, data={"grant_type":"client_credentials", "client_id":client_id, "client_secret":client_secret})
token = raw_token.json()
token = token["access_token"]

#do other stuff
while True:
    #print(configdata["schedules"].items())
    for k, v in configdata["schedules"].items():
        #print(type(v["action"]))
        #print(type(v["command"]))
        if v["time"] == datetime.datetime.now().strftime('%H:%M') and v["action"] != "None" and v["command"] == "None":
            print(1)
            requests.post(f'{server_ip_port}/proxy/daemon/server/{v["server_id"]}/{v["action"]}', headers={"Authorization":f"Bearer {token}"})
            print(v["action"] + " / " + v["server_id"])
        elif v["time"] == datetime.datetime.now().strftime('%H:%M') and v["action"] == "None" and v["command"] != "None":
            print(2)
            requests.post(f'{server_ip_port}/proxy/daemon/server/{v["server_id"]}/console', headers={"Authorization":f"Bearer {token}", "Content-Type":"application/json"}, data={"command":v["command"]})
            print(v["command"] + " / " + v["server_id"])

    time.sleep(60)