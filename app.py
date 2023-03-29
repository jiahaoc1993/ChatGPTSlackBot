import os
import re
import time
from threading import Thread

from revChatGPT.V3 import Chatbot
from slack_bolt import App
import logging
import sys

root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

ChatGPTConfig = {
    "api_key": os.getenv("OPENAI_API_KEY"),
}

if os.getenv("OPENAI_ENGINE"):
    ChatGPTConfig["engine"] = os.getenv("OPENAI_ENGINE")

app = App(logger=root)
chatbot = Chatbot(**ChatGPTConfig)

@app.command("/new")
def command_test(ack, say):
    global chatbot
    chatbot = Chatbot(**ChatGPTConfig)
    ack()
    say("session reset successfully.")

@app.event("app_mention")
def event_test(event, say):
    prompt = re.sub("\\s<@[^, ]*|^<@[^, ]*", "", event["text"])
    root.info(prompt)

    try:
        count = 0
        user = event["user"]
        original_message_ts = event["ts"]
        for response in chatbot.ask_stream(prompt):
            # only @ someone once
            if count == 0:
                send = f"<@{user}> {response}"
                count += 1
            else:
                send += f"{response}"
    except Exception as e:
        print(e)
        send = "we're experiencing exceptionally high demand. Please, try again."

    say(send, thread_ts=original_message_ts)

    

def chatgpt_refresh():
    while True:
        time.sleep(60)

if __name__ == "__main__":
    thread = Thread(target=chatgpt_refresh)
    thread.start()
    app.start(4000)  # POST http://localhost:4000/slack/events, event in your command configuration page.
