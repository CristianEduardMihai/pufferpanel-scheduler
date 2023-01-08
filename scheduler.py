import requests
import yaml
import os
import time
import datetime
import schedule

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

#print("Scheduler Started")

def execute_schedule():
    #if action
    if action != "None" and command == "None":
        token = get_token()
        requests.post(f'{server_ip_port}/proxy/daemon/server/{v["server_id"]}/{v["action"]}', headers={"Authorization":f"Bearer {token}"})
        print(f"Executed action {action} on server {server_id}")
    
    #if console command
    elif action == "None" and command != "None":
        token = get_token()
        requests.post(f'{server_ip_port}/proxy/daemon/server/{v["server_id"]}/console', headers={"Authorization":f"Bearer {token}", "Content-Type":"application/json"}, data={"command":v["command"]})
        print(f"Executed command {command} on server {server_id}")

print("Loading following schedules: ")
for k, v in configdata["schedules"].items():
    print(k + ": " + str(v["name"]))

    server_id = v["server_id"]
    action = v["action"]
    command = v["command"]
    day = v["day"]
    schedule_time = v["time"]

    if day == "all":
        schedule.every().day.at(schedule_time).do(execute_schedule)
    elif day == "monday":
        schedule.every().monday.at(schedule_time).do(execute_schedule)
    elif day == "tuesday":
        schedule.every().tuesday.at(schedule_time).do(execute_schedule)
    elif day == "wednesday":
        schedule.every().wednesday.at(schedule_time).do(execute_schedule)
    elif day == "thursday":
        schedule.every().thursday.at(schedule_time).do(execute_schedule)
    elif day == "friday":
        schedule.every().friday.at(schedule_time).do(execute_schedule)
    elif day == "saturday":
        schedule.every().saturday.at(schedule_time).do(execute_schedule)
    elif day == "sunday":
        schedule.every().sunday.at(schedule_time).do(execute_schedule)

print("\nSchedules loaded. They will be executed at the specified times.")

while True:
    schedule.run_pending()
    time.sleep(0.5)