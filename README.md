# Slack【日調】Bot

このSlack Botは、"【日調】" で始まるメッセージに反応して、そのメッセージにリアクションしていないチャンネルメンバーをメンションで通知します。

## 必要な設定

1. `.env` ファイルを作成し、以下の値を設定：
    ```
    SLACK_BOT_TOKEN=あなたのBotトークン
    SLACK_APP_TOKEN=あなたのアプリトークン
    ```

2. 依存のインストール：
    ```
    pip install -r requirements.txt
    ```

3. 実行：
    ```
    python main.py
    ```

## Botの動作
- チャンネルで「【日調】今日の進捗は？」などのメッセージを投稿すると、
- リアクションしていない人が自動でメンションされます。
# schedule_adjustment_slack
