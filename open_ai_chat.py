import logging
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging = logging.getLogger(__name__)


class OpenAIChat:
    PROMPT = {"role": "system", "content": "You are a helpful assistant, responding in a friendly and informative manner. When possible, be short and to the point. If you don't know the answer, you can say so. Don't hilusinate or make things up."}
    def __init__(self, chat_limit=30, model="gpt-4o-mini"):
        load_dotenv()
        self.client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.users = {}
        self.chat_limit = chat_limit
        self.model = model

    async def generate(self, text, user_id=None, model=None):
        if model is None:
            model = self.model
        if user_id not in self.users:
            messages = [
                self.PROMPT,
                {"role": "user", "content": text}
            ]
        else:
            messages = self.users[user_id] + [{"role": "user", "content": text}]

        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            )

        if user_id is not None:
            self.users[user_id] = messages + [{"role": "assistant", "content": response.choices[0].message.content}]
            if len(self.users[user_id]) > self.chat_limit:
                self.users[user_id] = [self.PROMPT] + self.users[user_id][-self.chat_limit:]
        return response.choices[0].message.content
    
    async def clear(self, user_id):
        if user_id in self.users:
            self.users.pop(user_id)
    
    async def transcript(self, file_name):
        audio_file= open(file_name, "rb")
        transcript = await self.client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            )
        audio_file.close()
        return transcript.text
    
    async def add_image(self, image_url, user_id):
        if user_id not in self.users:
            self.users[user_id] = [self.PROMPT]
        self.users[user_id].append({"role": "user", "content": [{"type": "image_url", "image_url": {"url": image_url}}]})

async def test_openai_chat():
    chat = OpenAIChat()
    user_id = "123"
    logging.info(await chat.generate("Who won the world series in 2020?", user_id))
    logging.info(await chat.generate("Where was it played?", user_id))

    await chat.clear(user_id)
    logging.info(await chat.generate("Where was it played?", user_id))

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_openai_chat())
