import os
import dotenv
import logging
import requests
import traceback
from logtail import LogtailHandler
from slack_bolt import App
from flask import Flask, request
from flask_cors import CORS
from slack_bolt.adapter.socket_mode import SocketModeHandler

import logging
logging.basicConfig(level=logging.DEBUG)

#Load local environment variables
dotenv.load_dotenv()
betterstack_token = os.getenv("BETTERSTACK_TOKEN")
server_url = os.getenv("SERVER_URL")
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET")

#BetterStack logger if token is provided
if betterstack_token:
  handler = LogtailHandler(source_token=betterstack_token)
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.INFO)
  logger.handlers = []
  logger.addHandler(handler)
  logger.info('bot_start')
  print("betterstack is ready")

slack_app = App(token=slack_bot_token, signing_secret=slack_signing_secret)

print("SLACK BOT IS READY")

def ask_server(message):

    data = {
    'message': message
    }
    # Send the POST request
    response = requests.post(server_url, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        answer = response.json()
        # Print the reply from the server
        print("Server replies successfully")
        #print(answer['reply'])
    else:
        print(f"Error: Received status code {response.status_code}")
        #print(response.text)

    print(answer["reply"].replace("<", "&lt;").replace(">", "&gt;"))
    return answer

@slack_app.event("app_home_opened")
def update_home_tab(client, event, logger):
  try:
    # views.publish is the method that your app uses to push a view to the Home tab
    client.views_publish(
      # the user that opened your app's app home
      user_id=event["user"],
      # the view object that appears in the app home
      view={
        "type": "home",
        "callback_id": "home_view",

        # body of the view
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Welcome to Virtuozzo Hybrid Infrastructure Bot * :tada:"
            }
          },
          {
            "type": "divider"
          },
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "Please ask any question related to Virtuozzo Hybrid Infrastructure, for example:\n How to create Kubernetes storage class?"
            }
          },
        ]
      }
    )

  except Exception as e:
    logger.error(f"Error publishing home tab: {e}")

@slack_app.command("/hello")
def hello(body, ack):
    ack(f"Hi <@{body['user_id']}>!")

@slack_app.event("message")
def handle_message(event, say):
    try:
      user_id = event['user']
      message = event['text']
      answer = ask_server(message)
      say(answer["reply"].replace("<", "&lt;").replace(">", "&gt;"))
    except Exception as e:
      print(f"Error: {str(e)}\nTraceback: {traceback.format_exc()}")
      say("An error occurred. Please try again later.")

if __name__ == '__main__':
    SocketModeHandler(slack_app, slack_bot_token).start()
  
