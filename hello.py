import os
from dotenv import load_dotenv
from google import genai

load_dotenv()  # reads the .env file
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Give me one funny reel hook about Bangalore traffic."
)

print(response.text)