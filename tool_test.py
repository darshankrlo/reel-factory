import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def save_file(filename: str, content: str) -> str:
    """Saves text content to a file in the output folder.

    Args:
        filename: Name of the file, like hook.txt
        content: The text to write into the file
    """
    os.makedirs("output", exist_ok=True)
    path = os.path.join("output", os.path.basename(filename))
    with open(path, "w") as f:
        f.write(content)
    print(f"[TOOL RAN] saved {path}")
    return f"Saved to {path}"

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Write one funny reel hook about Bangalore traffic and save it to a file called hook.txt",
    config=types.GenerateContentConfig(tools=[save_file]),
)

print(response.text)