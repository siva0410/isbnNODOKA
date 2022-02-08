from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os

from server import getBookInfo

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    isbn = event.message.text.strip()
    db = getBookInfo(isbn)
    sendMessage = """ISBN :isbn
タイトル：:title
著者：:author
出版社：:publisher
発行年月日：:pubdate
を登録したよ！
""", {'isbn': db['properties']['ISBN']['rich_text'][0]['text']['content'],
      'title': db['properties']['タイトル']['title'][0]['text']['content'],
      'author': db['properties']['著者']['rich_text'][0]['text']['content'],
      'publisher': db['properties']['出版社']['select']['name'],
      'pubdate': db['properties']['発行年月日']['date']['start'],
}
    line_bot_api.reply_message(
        event.reply_token,
        [TextSendMessage(text=sendMessage), TextSendMessage(text=db['properties']['表紙']['files'][0]['external']['url'])]
    )


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
