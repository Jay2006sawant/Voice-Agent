# Voice Agent Assignment Solution

This project implements a voice-enabled AI agent that manages a To-Do list with tool-based CRUD operations and stores important user memories.

## Features

- Voice input (speech-to-text) and voice output (text-to-speech)
- Tool-based To-Do management:
  - Add task
  - Update task (title/status)
  - Delete task
  - List tasks
- Memory system:
  - Stores important user events
  - Recalls relevant memories on request
- Agent behavior:
  - Uses OpenAI function-calling if `OPENAI_API_KEY` is available
  - Falls back to deterministic local intent handling

## Project Structure

- `main.py` - interactive voice app loop
- `voice_agent/voice.py` - STT/TTS handling
- `voice_agent/todo_tools.py` - JSON-backed To-Do CRUD tools
- `voice_agent/memory.py` - memory capture and recall
- `voice_agent/agent.py` - prompt + function-calling/tool orchestration
- `tests/test_todo_memory.py` - basic tests

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If `PyAudio` fails to install on Linux, install system packages first:

```bash
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio
```

## Run

```bash
python main.py
```

### Example voice commands

- "Add task prepare assignment video"
- "List my todos"
- "Mark task `abcd1234` done"
- "Delete task `abcd1234`"
- "Remember that my exam is on Tuesday"
- "What do you remember about exam?"

## OpenAI Function Calling (Optional)

Set your API key to enable LLM-based function selection and natural responses:

```bash
export OPENAI_API_KEY="your_key_here"
```

Without API key, the app still works using local rule-based logic.

## Test

```bash
pytest -q
```

## Assignment Coverage

- Voice interface: implemented with STT/TTS + typed fallback
- Tool usage: add/update/delete/list fully implemented
- Memory: stores and recalls important interactions
- Prompt + function calling: in `VoiceTodoAgent.SYSTEM_PROMPT` and `_process_with_openai`
- Code structure: modular components for voice, tools, memory, and agent

## Demo Video Checklist (6-10 min)

- Show your face and screen
- Start app and issue voice commands
- Demonstrate all 4 CRUD operations
- Demonstrate memory save + recall
- Briefly explain project structure and prompt logic
