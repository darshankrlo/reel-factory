import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from ddgs import DDGS

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def search_trends(topic: str) -> str:
    """Searches the web for current trends, popular formats and ideas about a topic.

    Args:
        topic: What to search for, like 'Bangalore street food reels trending'
    """
    print(f"[TOOL RAN] searching: {topic}")
    try:
        results = DDGS().text(topic, max_results=5)
        if not results:
            return "Search returned no results. Try a shorter or different query, or tell the user no trend data was found."
        lines = [f"- {r['title']}: {r['body']}" for r in results]
        return "\n".join(lines)
    except Exception as e:
        return f"Search failed with error: {e}. Do not invent trend data; tell the user the search failed."

def save_file(filename: str, content: str) -> str:
    """Saves text content to a file in the output folder.

    Args:
        filename: Name of the file, like script.txt
        content: The text to write into the file
    """
    os.makedirs("output", exist_ok=True)
    path = os.path.join("output", os.path.basename(filename))
    with open(path, "w") as f:
        f.write(content)
    print(f"[TOOL RAN] saved {path}")
    return f"Saved to {path}"

topic = input("Reel topic: ")

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=f"Make a reel package about: {topic}. First call search_trends using "
             f"exactly this topic as the query, with no extra words: '{topic}'. "
             f"Then write a hook, a short script, a shot list and captions, "
             f"and save everything to reel.txt",
    config=types.GenerateContentConfig(tools=[search_trends, save_file]),
)

print(response.text)