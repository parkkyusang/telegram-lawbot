import os
from telethon import TelegramClient, events
from openai import OpenAI

# 환경변수 로드
api_id = int(os.environ["TELEGRAM_API_ID"])
api_hash = os.environ["TELEGRAM_API_HASH"]
bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
openai_api_key = os.environ["OPENAI_API_KEY"]

# 광고 문구 불러오기
ad_path = "ad.txt"
if os.path.exists(ad_path):
    with open(ad_path, encoding="utf-8") as f:
        ADVERTISEMENT = "\n\n" + f.read().strip()
else:
    ADVERTISEMENT = ""

# 시스템 프롬프트 불러오기
instruction_path = "instruction.txt"
if os.path.exists(instruction_path):
    with open(instruction_path, encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read().strip()
else:
    SYSTEM_PROMPT = ""

# 텔레그램 클라이언트 및 GPT 세팅
client = TelegramClient("lawbot", api_id, api_hash).start(bot_token=bot_token)
gpt = OpenAI(api_key=openai_api_key)

@client.on(events.NewMessage)
async def handler(event):
    if event.out:
        return  # 무한 루프 방지

    question = event.raw_text.strip()
    if question:
        response = gpt.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ]
        )
        full_reply = response.choices[0].message.content + ADVERTISEMENT
        await event.reply(full_reply)

client.run_until_disconnected()
