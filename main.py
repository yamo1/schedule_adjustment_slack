from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os

app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.event("message")
def handle_message_events(body, say, client):
    event = body.get("event", {})
    text = event.get("text", "")
    
    if text.startswith("【日調】") and "subtype" not in event:
        channel_id = event["channel"]
        ts = event["ts"]

        members_resp = client.conversations_members(channel=channel_id)
        members = set(members_resp["members"])

        reactions_resp = client.reactions_get(channel=channel_id, timestamp=ts)
        reactions = reactions_resp["message"].get("reactions", [])
        reacted_users = set()
        for reaction in reactions:
            reacted_users.update(reaction.get("users", []))

        unreacted = members - reacted_users

        if unreacted:
            mentions = " ".join([f"<@{uid}>" for uid in unreacted])
            say(text=f"リアクションまだの人：{mentions}", thread_ts=ts)
        else:
            say(text="全員リアクション済みです！", thread_ts=ts)


import threading
from flask import Flask

# FlaskでダミーのWebサーバーを動かす
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Slack bot is running!"

def start_flask():
    flask_app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    # Flaskサーバーは別スレッドで
    threading.Thread(target=start_flask).start()

    # Slack Socket Mode
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
