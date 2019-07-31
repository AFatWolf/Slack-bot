import os
import slack
import ssl as ssl_lib
import certifi
import json
import datetime
state = {}
working_time = {}
start_time = {}
end_time = {}
def convertTime(working_time: str):
    total_second = working_time.total_seconds()
    hours = int(total_second/3600)
    total_second-=hours*3600
    minutes = int(total_second/60)
    total_second-=minutes*60
    seconds = int(total_second) 
    return str(hours) + " giờ " + str(minutes) + " phút " + str(seconds) + " giây."

def Mess(web_client: slack.WebClient, user_id: str, channel_id: str, mess: str):
    message = {}
    message["channel"] = channel_id
    message["username"] = "Euler"
    message["text"] = mess
    web_client.chat_postMessage(**message)
 
@slack.RTMClient.run_on(event="message")
def reply(**payload):
    data = payload["data"]
    web_client = payload["web_client"]
    channel_id = data.get("channel")
    user_id = data.get("user")
    text = data.get("text")
    global state
    global start_time
    global end_time
    global working_time 
    if ((user_id in state) == False):
        state[user_id] = 0
        working_time[user_id] = datetime.timedelta(0)
    if text and text.lower() == "ci":
        if (state[user_id] == 0):
            state[user_id] = 1
            start_time[user_id] = datetime.datetime.now() 
            mess = "<@{}>".format(user_id) + "Hãy cùng nhau làm việc nào."
        else:
            mess = "Bạn đã checkin rồi!"
        return Mess(web_client, user_id, channel_id, mess)
    # check out. 
    if text and text.lower() == "co":
        if (state[user_id] == 1):
            state[user_id] = 0
            mess = "Bạn đã vất vả rồi"
            end_time[user_id] = datetime.datetime.now()
            working_time[user_id] += end_time[user_id] - start_time[user_id]
        else:
            mess = "Bạn đã checkout rồi!"
        return Mess(web_client, user_id, channel_id,mess)
    if text and text.lower() == "gl":
        mess = "Bạn đã làm việc trong: " + convertTime(working_time[user_id])
        return Mess(web_client, user_id, channel_id, mess)
 
if __name__ == "__main__":
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    slack_token = os.environ["SLACK_BOT_TOKEN"]
    rtm_client = slack.RTMClient(token=slack_token, ssl=ssl_context)
    rtm_client.start()
