# Reel Factory

An AI agent that researches a topic and writes a complete short-form reel package: hook, script, shot list and captions. Built in Python with the Gemini API.

## What it does

You type a topic. The agent:
1. Searches the web for the topic using a `search_trends` tool
2. Writes a hook, a short script, a shot list and captions
3. Saves everything to `output/reel.txt` using a `save_file` tool

## How it works

The model never runs tools itself. It asks for a tool, my Python code runs it, and the result is sent back to the model. `agent_v2.py` implements this loop by hand:

- The full conversation (`contents`) is resent on every model call, because the model keeps no memory between calls
- The model decides when it's finished by replying with no tool request
- A step cap (`range(8)`) stops a confused agent from looping forever
- `save_file` only writes inside the `output/` folder

`agent_v1.py` is the same agent using the SDK's automatic tool loop.

## Setup

```bash
git clone https://github.com/<your-username>/reel-factory.git
cd reel-factory
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

Create a `.env` file with your own free key from Google AI Studio:

```
GEMINI_API_KEY=your_key_here
```

## Run

```bash
python agent_v2.py
```

## Files

- `agent_v2.py`: the agent with a hand-written loop
- `agent_v1.py`: the agent using automatic tool calling
- `hello.py`, `tool_test.py`: early experiments (first API call, first tool)
- `list_models.py`: lists the models your key can use

## What I learned

- Agents are an LLM plus tools plus a loop
- Tool return values are the only thing the model sees about what happened
- Model names change often, so check the model list when a call fails

## Next

- More tools and a system instruction
- Retrieval over my own notes (RAG)