from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage
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
    sendMessage = """ISBN {0[isbn]}
タイトル：{0[title]}
著者：:{0[author]}
出版社：{0[publisher]}
発行年月日：{0[pubdate]}
""".format({'isbn': db[0]["summary"]["isbn"],
      'title': db[0]["summary"]["title"],
      'author': db[0]["summary"]["author"],
      'publisher': db[0]["summary"]["publisher"],
      'pubdate': db[0]["summary"]["pubdate"]
})
    line_bot_api.reply_message(
        event.reply_token,
        [TextSendMessage(text=sendMessage+"を登録したよ！"), ImageSendMessage(original_content_url=db[0]["summary"]["cover"], preview_image_url=db[0]["summary"]["cover"])]
    )    


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
