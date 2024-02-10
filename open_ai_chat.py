import os
from dotenv import load_dotenv
from openai import AsyncOpenAI


class OpenAIChat:
    PROMPT = {"role": "system", "content": "You are a helpful assistant, responding in a friendly and informative manner, but don't go too long."}
    def __init__(self, chat_limit=10):
        load_dotenv()
        self.client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.users = {}

    async def generate(self, text, user_id=None):
        if user_id not in self.users:
            messages = [
                self.PROMPT,
                {"role": "user", "content": text}
            ]
        else:
            messages = self.users[user_id] + [{"role": "user", "content": text}]

        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            )
        if user_id is not None:
            self.users[user_id] = messages + [{"role": "assistant", "content": response.choices[0].message.content}]
            if len(self.users[user_id]) > 10:
                self.users[user_id] = [self.PROMPT] + self.users[user_id][-10:]
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

async def test_openai_chat():
    chat = OpenAIChat()
    user_id = "123"
    print(await chat.generate("Who won the world series in 2020?", user_id))
    print(await chat.generate("Where was it played?", user_id))

    await chat.clear(user_id)
    print(await chat.generate("Where was it played?", user_id))

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_openai_chat())
