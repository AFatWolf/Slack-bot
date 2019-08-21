import os
import slack
import ssl as ssl_lib
import certifi
import json
import datetime
from user import user
from coverFinder import CoverFinder
import re
from BookStationDialogue import bookStationDialogue

workers = {}

def check_in(web_client: slack.WebClient, user_id: str, channel_id: str):
    workers[user_id].check_in()
    
    message = {}
    message["channel"] = channel_id
    message["username"] = "OfficeBot"
    message["text"] = "Hello <@{0}>. Have a nice day!".format(user_id)
    web_client.chat_postMessage(**message)

def check_out(web_client: slack.WebClient, user_id: str, channel_id: str):
    message = {}
    message["channel"] = channel_id
    message["username"] = "OfficeBot"
    
    if user_id not in workers or not workers[user_id].isWorking(): 
        message["text"] = "You have not check in yet!"
    else:
        workers[user_id].check_out()
        for key in workers.keys():
                print(f"Key {key}")

        bye_sentence = ""
        if workers[user_id].get_working_hours() <= 5:
                bye_sentence = "No salary if not 5 hours you know?"
        else:
                bye_sentence = "Great job!"

        message["text"] = "Bye <@{0}>.\nYou have worked {1:.2f} hours today!\n{2}".format(user_id, workers[user_id].get_working_hours(), bye_sentence)
    web_client.chat_postMessage(**message)

def get_working_hours(web_client: slack.WebClient, user_id: str, channel_id: str):
    message = {}
    message["channel"] = channel_id
    message["username"] = "OfficeBot"
    
    if user_id not in workers.keys(): 
        message["text"] = "You have not check in yet!"
    else:
        message["text"] = "<@{0}>! You have worked for {1:.2f} hours until now.".format(user_id, workers[user_id].get_working_hours())
   
    web_client.chat_postMessage(**message)

def put_book_cover(web_client: slack.WebClient, user_id: str, channel_id: str, book_name: str):
    book_info = CoverFinder(book_name).getBookCoverUrl()
    print("------Book Info--------------\n{0}".format(book_info))
    message = {}
    message['channel'] = channel_id
    message['username'] = 'librarian'
    message['attachments'] = [{'pretext': "Is this the book that you mentioned before?",
                                'color': 'good',
                                **book_info}]
    web_client.chat_postMessage(**message)

dia = {}

@slack.RTMClient.run_on(event="message")
def reply(**payload):
    data = payload["data"]
    print("-" * 40)
    print("Type: {} \n".format(type(payload)))
    print("Here comes the data:\n", payload)
    print("-" * 40)
    web_client = payload["web_client"]
    channel_id = data.get("channel")
    user_id = data.get("user")
    text = data.get("text")
    
    # create user
    if user_id not in workers:
        workers[user_id] = user(user_id, channel_id)
        dia[user_id] = None

    if dia[user_id] == None:
        if text and "ci" in text.lower():
            return check_in(web_client, user_id, channel_id)
        if text and "co" in text.lower():
            return check_out(web_client, user_id, channel_id)
        if text and "gl" in text.lower():
            return get_working_hours(web_client, user_id, channel_id)
        if text and re.search(r"^bf", text):
            # strip the command 
            text = re.sub(r"^bf\s*", "", text)
            print(text)
            # reduce space
            book_name = " ".join(text.split(" "))
            print("Book name: {0}".format(book_name))
            return put_book_cover(web_client, user_id, channel_id, book_name)
        
        if text and re.search(r"^book", text):
            dia[user_id] = bookStationDialogue(workers[user_id])
            reply = dia[user_id].getReply(text)
            web_client.chat_postMessage(**reply)
    else:
        reply = dia[user_id].getReply(text)
        web_client.chat_postMessage(**reply)
        # to see if it is quit or not
        if dia[user_id].haveEmptyHandler():
            dia[user_id] = None
    

if __name__ == "__main__":
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    slack_token = os.environ["SLACK_BOT_TOKEN"]
    rtm_client = slack.RTMClient(token=slack_token, ssl=ssl_context)
    rtm_client.start()