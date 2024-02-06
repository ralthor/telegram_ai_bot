import os
from dotenv import load_dotenv
from openai import OpenAI


class OpenAIChat:
    PROMPT = {"role": "system", "content": "You are a helpful assistant, responding in a friendly and informative manner, but in short sentences."}
    def __init__(self, chat_limit=10):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.users = {}

    def generate(self, text, user_id=None):
        if user_id not in self.users:
            messages = [
                self.PROMPT,
                {"role": "user", "content": text}
            ]
        else:
            messages = self.users[user_id] + [{"role": "user", "content": text}]

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            )
        if user_id is not None:
            self.users[user_id] = messages + [{"role": "assistant", "content": response.choices[0].message.content}]
            if len(self.users[user_id]) > 10:
                self.users[user_id] = [self.PROMPT] + self.users[user_id][-10:]
        return response.choices[0].message.content
    
    def clear(self, user_id):
        if user_id in self.users:
            self.users.pop(user_id)
    
    def transcript(self, file_name):
        audio_file= open(file_name, "rb")
        transcript = self.client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            )
        audio_file.close()
        return transcript.text

if __name__ == "__main__":
    chat = OpenAIChat()
    user_id = "123"
    print(chat.generate("Who won the world series in 2020?", user_id))
    print(chat.generate("Where was it played?", user_id))

    chat.clear(user_id)
    print(chat.generate("Where was it played?", user_id))
