# 🎙️ Voice AI Agent - Technical Recruiter

An autonomous, ultra-low latency AI voice agent designed to conduct technical HR screening interviews. The agent speaks naturally, handles user interruptions (barge-in), dynamically adjusts its questions based on candidate answers, and autonomously scores the interview in real-time.

## 🚀 Key Features

* **Real-Time Voice Orchestration:** Achieves sub-second response times using WebRTC audio streaming.
* **Agentic Function Calling:** Uses custom Python tools triggered by the LLM to analyze candidate answers and save structured summaries and scores directly to a local CSV file.
* **Dynamic Conditional Logic:** The agent adapts its interview flow based on context (e.g., asking specific follow-up questions only if the candidate mentions deployment experience).
* **Interruption Handling (Barge-in):** Instantly stops speaking and listens when the user interrupts the conversation.

## 🛠️ Tech Stack

* **Framework:** [LiveKit Agents](https://docs.livekit.io/agents/) (Python)
* **Voice Activity Detection (VAD):** Silero
* **Speech-to-Text (STT):** Deepgram (Nova-3)
* **LLM / Reasoning:** OpenAI (GPT-4o-mini)
* **Text-to-Speech (TTS):** Cartesia (Sonic-3)

## 📁 Project Structure

```text
voice_AI_Agent/
├── agent.py               # Main agent logic and pipeline orchestration
├── requirements.txt       # Python dependencies
├── .env.local             # Environment variables (not committed)
└── README.md
