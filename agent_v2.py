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

prompt = (f"Make a reel package about: {topic}. First call search_trends using "
          f"exactly this topic as the query: '{topic}'. Then write a hook, a short "
          f"script, a shot list and captions, and save everything to reel.txt")

tool_map = {"search_trends": search_trends, "save_file": save_file}

config = types.GenerateContentConfig(
    tools=[search_trends, save_file],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)

contents = [types.Content(role="user", parts=[types.Part(text=prompt)])]

for step in range(8):  # safety cap: never loop forever
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite", contents=contents, config=config
    )
    calls = response.function_calls
    if not calls:                      # no tool requested = the model is done
        print(response.text)
        break

    contents.append(response.candidates[0].content)   # remember what the model said
    result_parts = []
    for call in calls:
        print(f"[MODEL ASKED] {call.name}({call.args})")
        result = tool_map[call.name](**call.args) 
        print(f"[TOOL RESULT] {str(result)[:500]}")     # YOUR code runs the tool
        result_parts.append(
            types.Part.from_function_response(name=call.name, response={"result": result})
        )
    contents.append(types.Content(role="user", parts=result_parts))  # send results back