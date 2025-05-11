from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
import threading
from flask import Flask

app = App(token=os.environ["SLACK_BOT_TOKEN"])

# メッセージの timestamp を保存（スレッド追跡用）
reminder_message_ts_map = {}

@app.event("message")
def handle_message_events(body, say, client):
    event = body.get("event", {})
    text = event.get("text", "")
    
    if text and text.startswith("【日調】"):
        channel_id = event["channel"]
        original_ts = event["ts"]

        # チャンネルメンバーを取得
        members_resp = client.conversations_members(channel=channel_id)
        members = set(members_resp["members"])

        # リアクション取得
        reactions_resp = client.reactions_get(channel=channel_id, timestamp=original_ts)
        reactions = reactions_resp["message"].get("reactions", [])
        reacted_users = set()
        for reaction in reactions:
            reacted_users.update(reaction.get("users", []))

        # 未リアクション者
        unreacted = members - reacted_users

        if unreacted:
            mentions = " ".join([f"<@{uid}>" for uid in unreacted])
            response = client.chat_postMessage(
                channel=channel_id,
                text=f"リアクションまだの人：{mentions}",
                thread_ts=original_ts
            )
            reminder_message_ts_map[original_ts] = response["ts"]
        else:
            client.chat_postMessage(
                channel=channel_id,
                text="全員リアクション済みです！",
                thread_ts=original_ts
            )

@app.event("reaction_added")
def handle_reaction_added_events(body, client):
    event = body.get("event", {})
    item = event.get("item", {})
    channel_id = item.get("channel")
    original_ts = item.get("ts")

    if not original_ts or original_ts not in reminder_message_ts_map:
        return  # 対象外のリアクション

    # 再チェックして未リアクション者を更新
    members_resp = client.conversations_members(channel=channel_id)
    members = set(members_resp["members"])

    reactions_resp = client.reactions_get(channel=channel_id, timestamp=original_ts)
    reactions = reactions_resp["message"].get("reactions", [])
    reacted_users = set()
    for reaction in reactions:
        reacted_users.update(reaction.get("users", []))

    unreacted = members - reacted_users

    reminder_ts = reminder_message_ts_map[original_ts]

    if unreacted:
        mentions = " ".join([f"<@{uid}>" for uid in unreacted])
        client.chat_update(
            channel=channel_id,
            ts=reminder_ts,
            text=f"リアクションまだの人：{mentions}"
        )
    else:
        client.chat_update(
            channel=channel_id,
            ts=reminder_ts,
            text="全員リアクション済みです！"
        )
        del reminder_message_ts_map[original_ts]  # 登録解除

# FlaskでRenderのポート問題回避
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Slack bot is running!"

def start_flask():
    flask_app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    threading.Thread(target=start_flask).start()
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
