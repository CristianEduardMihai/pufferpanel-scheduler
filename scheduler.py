import requests
import yaml
import os
import time
import datetime

#get config data
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
def get_token():
    raw_token = requests.post(server_ip_port + "/oauth2/token", headers={"Content-Type":"application/x-www-form-urlencoded"}, data={"grant_type":"client_credentials", "client_id":client_id, "client_secret":client_secret})
    token = raw_token.json()
    token = token["access_token"]
    return token

#initiate the executed actions list
executed_actions = []
#initiate the list cleanup counter
list_counter = 0

print("Scheduler Started")

#do other stuff
while True:
    #print(configdata["schedules"].items())
    for k, v in configdata["schedules"].items():
        #print(type(v["action"]))
        #print(type(v["command"]))

        action_time = v["time"]
        action_time = action_time.split(":")

        now_time = datetime.datetime.now().strftime('%H:%M:%S')
        now_time = now_time.split(":")



        action_hours = int(action_time[0])
        action_minutes = int(action_time[1])
        action_seconds = int(action_time[2])

        now_hours = int(now_time[0])
        now_minutes = int(now_time[1])
        now_seconds = int(now_time[2])

        #------if action

        # long block of text, time to break it down
        # if the action hour is equal to the current hour
        # and the action minute is equal to the current minute
        # and the action second is equal to the current second or the current second + 1
        # and the action is not equal to None
        # then execute the action/command(as in the elif statement below)      
        if (action_hours == now_hours and action_minutes == now_minutes and (action_seconds == now_seconds or action_seconds == now_seconds+1)) and v["action"] != "None" and v["command"] == "None":
            # if the action has not yet been executed
            if v["action"] + "_" + v["server_id"] not in executed_actions:
                token = get_token()
                requests.post(f'{server_ip_port}/proxy/daemon/server/{v["server_id"]}/{v["action"]}', headers={"Authorization":f"Bearer {token}"})
                print(v["action"] + " / " + v["server_id"])
                #set the action as executed
                executed_actions.append(v["action"] + "_" + v["server_id"])
        
        #------if console command
        elif (action_hours == now_hours and action_minutes == now_minutes and (action_seconds == now_seconds or action_seconds == now_seconds+1)) and v["action"] == "None" and v["command"] != "None":
            if v["command"] + "_" + v["server_id"] not in executed_actions:
                token = get_token()
                requests.post(f'{server_ip_port}/proxy/daemon/server/{v["server_id"]}/console', headers={"Authorization":f"Bearer {token}", "Content-Type":"application/json"}, data={"command":v["command"]})
                print(v["command"] + " / " + v["server_id"])
                #set the action as executed
                executed_actions.append(v["command"] + "_" + v["server_id"])
        
        #clean the executed actions list every 10 seconds
        list_counter = list_counter + 1
        if list_counter == 20:
            executed_actions = []
            list_counter = 0

    time.sleep(0.5)