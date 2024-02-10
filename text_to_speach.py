import aiohttp
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from enum import Enum as enum


class TextToSpeech:
    class Model(enum):
        Normal = "tts-1"
        HighDefinition = "tts-1-hd"


    class Voice(enum):
        Alloy = "alloy"
        Echo = "echo"
        Fable = "fable"
        Onyx = "onyx"
        Nova = "nova"
        Shimmer = "shimmer"
        Twinkle = "twinkle"
    def __init__(self, voice=Voice.Shimmer.value, model=Model.Normal.value):
        self.voice = voice
        self.model = model
        self.headers = {
            "Authorization": "Bearer " + os.getenv('OPENAI_API_KEY'),
            "Content-Type": "application/json"
        }

    async def generate(self, text, voice=None, model=None, file_name="speech.mp3"):
        data = {
            "model": model if model else self.model,
            "input": text,
            "voice": voice if voice else self.voice
        }
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.openai.com/v1/audio/speech', headers=self.headers, data=json.dumps(data)) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"Failed to generate speech: {response.status} - {text}")
                data = await response.read()
                with open(file_name, 'wb') as f:
                    f.write(data)
        return response

def convert_day_to_text(day):
    day = int(day)
    days = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth",
            "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth",
            "nineteenth", "twentieth", "twenty-first", "twenty-second", "twenty-third", "twenty-fourth",
            "twenty-fifth", "twenty-sixth", "twenty-seventh", "twenty-eighth", "twenty-ninth", "thirtieth",
            "thirty-first"]
    return days[day - 1]


def convert_month_to_text(month):
    month = int(month)
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
              "November", "December"]
    return months[month - 1]


async def test_tts():
    load_dotenv()
    time_now = datetime.now().strftime("%H and %M minutes and %S seconds.")
    curern_day = datetime.now().strftime("%d")
    current_month = datetime.now().strftime("%m")
    current_year = datetime.now().strftime("%Y")
    sample_text = f"This is the {convert_day_to_text(curern_day)} of {convert_month_to_text(current_month)}, {current_year}, and time is {time_now}. The quick brown fox jumps over the lazy dog. This is a sample text to test the tts conversion."

    tts = TextToSpeech()
    await tts.generate(sample_text, file_name="speech4.mp3")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_tts())
