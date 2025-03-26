import os
import random
from telethon import TelegramClient, events
from openai import OpenAI

# 환경변수 로드
api_id = int(os.environ["TELEGRAM_API_ID"])
api_hash = os.environ["TELEGRAM_API_HASH"]
bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
openai_api_key = os.environ["OPENAI_API_KEY"]

# 텔레그램 & GPT 설정
client = TelegramClient("lawbot", api_id, api_hash).start(bot_token=bot_token)
gpt = OpenAI(api_key=openai_api_key)

# 광고 랜덤 선택
def get_random_ad():
    try:
        with open("ads.txt", encoding="utf-8") as f:
            ads = [line.strip() for line in f if line.strip()]
            return "\n\n" + random.choice(ads)
    except:
        return ""

# 시스템 프롬프트 로딩
instruction_path = "instruction.txt"
if os.path.exists(instruction_path):
    with open(instruction_path, encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read().strip()
else:
    SYSTEM_PROMPT = ""

# RAG: 관련 법령 문장 추출
def search_law_snippets(query, top_k=3):
    import difflib
    docs = []
    for fname in os.listdir("laws"):
        if fname.endswith(".txt"):
            with open(os.path.join("laws", fname), encoding="utf-8") as f:
                lines = [line.strip() for line in f if len(line.strip()) > 20]
                matches = difflib.get_close_matches(query, lines, n=top_k, cutoff=0.3)
                docs.extend(matches)
    return "\n".join(docs[:top_k])

@client.on(events.NewMessage)
async def handler(event):
    if event.out:
        return

    query = event.raw_text.strip()
    if not query:
        return

    snippets = search_law_snippets(query)
    ad = get_random_ad()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"질문: {query}\n\n참고 법령:\n{snippets}"}
    ]

    response = gpt.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    full_reply = response.choices[0].message.content + ad
    await event.reply(full_reply)

client.run_until_disconnected()
