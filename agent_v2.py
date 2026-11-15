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
    
def check_hook(hook: str) -> str:
    """Checks whether a reel hook is short enough to work in the first 3 seconds.
    Always call this on your hook before saving the final reel.

    Args:
        hook: The hook text to check
    """
    words = len(hook.split())
    print(f"[TOOL RAN] check_hook: {words} words")
    if words > 10:
        return f"FAIL: the hook is {words} words. Rewrite it in 12 words or fewer and check again."
    return f"PASS: the hook is {words} words."

def choose(question, options):
    print(f"\n{question}")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    while True:
        answer = input("Pick a number: ").strip()
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return options[int(answer) - 1]
        print("Please enter one of the numbers above.")

topic = input("Reel topic: ")

reel_type = choose("Which type of reel?", [
    "Educational (teach one thing)",
    "Storytelling (a mini story)",
    "Comedy skit",
    "Motivational",
])
tone = choose("Which tone?", ["Funny", "Serious", "Emotional", "High-energy hype"])
length = choose("How long should the reel be?", ["15 seconds", "30 seconds", "60 seconds"])

seconds = int(length.split()[0])
max_words = int(seconds * 2.5)   # people speak roughly 2.5 words per second

prompt = (f"Make a reel package about: {topic}. "
          f"Reel type: {reel_type}. Tone: {tone}. Length: {length}. "
          f"First call search_trends using exactly this topic as the query: '{topic}'. "
          f"Then write a hook, a script of at most {max_words} words so it fits {length}, "
          f"a shot list and captions, and save everything to reel.txt")

tool_map = {"search_trends": search_trends, "save_file": save_file, "check_hook": check_hook}

config = types.GenerateContentConfig(
    tools=[search_trends, save_file, check_hook],
    system_instruction=(
        "You are Reel Factory, a content research agent. Work in this order: "
        "1) search for trends, 2) draft the full reel, 3) call check_hook on your hook "
        "and rewrite it until it passes, 4) save the final reel with save_file. "
        "If a tool reports a failure, begin your final answer by saying which tool failed. "
        "Never invent trend data or present guesses as research."
    ),
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