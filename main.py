import os
from telethon import TelegramClient, events
from openai import OpenAI

api_id = int(os.environ["TELEGRAM_API_ID"])
api_hash = os.environ["TELEGRAM_API_HASH"]
bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
openai_api_key = os.environ["OPENAI_API_KEY"]

client = TelegramClient("lawbot", api_id, api_hash).start(bot_token=bot_token)
gpt = OpenAI(api_key=openai_api_key)

@client.on(events.NewMessage)
async def handler(event):
    if event.out:
        return  # 🛑 내가 보낸 메시지는 무시!

    question = event.raw_text.strip()
    if question:
        response = gpt.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}]
        )
        await event.reply(response.choices[0].message.content)

client.run_until_disconnected()
