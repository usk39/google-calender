from flask import Flask, request, abort
import os

import quickstart

from linebot import (
   LineBotApi, WebhookHandler
)
from linebot.exceptions import (
   InvalidSignatureError
)
from linebot.models import (
   MessageEvent, PostbackEvent, TextMessage, TextSendMessage,
   QuickReplyButton, QuickReply, PostbackAction, DatetimePickerAction
)

app = Flask(__name__)

# 環境変数からLINE Access Tokenを設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
# 環境変数からLINE Channel Secretを設定
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


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
   push_text = event.message.text
   text = quickstart.extract_words(push_text)
   if text is None:
       text_message = TextSendMessage(text="Googleカレンダーの予定を知りたいですか？それとも追加したいですか？",
                                      quick_reply=QuickReply(items=[
                                          QuickReplyButton(action=DatetimePickerAction(
                                              label="予定を知りたい", data="read", mode="date")),
                                          QuickReplyButton(action=PostbackAction(
                                              label="予定を追加したい", data="write"))
                                      ]))
       line_bot_api.reply_message(event.reply_token, text_message)
   else:
       htmllink = quickstart.write(*text)
       line_bot_api.reply_message(event.reply_token, TextSendMessage(text=htmllink))

@handler.add(PostbackEvent)
def handle_postback(event):
   if event.postback.data == "read":
       date = event.postback.params['date']
       msg = quickstart.read(date)
       line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
   else event.postback.data == "write":
       text_write = "以下の形式で追加したい予定を入力してください。"\
                    "入力形式が正しくない場合、最初のクイックリプライに戻ります。追加に成功した場合はURLが表示されます。"\
                    "\n予定名\n場所(任意)\n年月日(半角数字8桁)\n開始時間(半角数字4桁)\n終了時間(半角数字4桁)"
       line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text_write))

if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
