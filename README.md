# 🧠 AI Tools Digest Chatbot (LangGraph + Azure OpenAI + Microsoft Teams)

A conversational chatbot built with **LangGraph** and **Azure OpenAI** that:

1. Chats normally like a regular AI assistant.  
2. When told _“send the new tools to the team”_, it:
   - Finds the latest AI tools launched this week using **SerpAPI**.
   - Summarizes them with **Azure OpenAI**.
   - Sends the digest directly to your **Microsoft Teams** channel via an **Incoming Webhook**.

---

## 📌 Features
- **Interactive chat** with context.
- **Automated AI tool discovery** from the last 7 days.
- **GPT-powered summaries** with tool name, website, features, pricing, and category.
- **One-command Teams integration** — just type the request and it posts to your team.
- Fully configurable via `.env` file.

---

## 📂 Project Structure
.
├── langgraph_bot.py       # Chatbot entry point (LangGraph workflow)
├── fetch.py               # Tool search & summarization logic
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not committed to repo)
└── ai_tools_weekly_digest.txt  # Last generated digest (local save)

---

## ⚙️ Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/ai-tools-chatbot.git
cd ai-tools-chatbot

### 2. Install dependencies
pip install -r requirements.txt

### 3. Create .env file

# SerpAPI for Google Search
SERPAPI_KEY=your_serpapi_key

# Azure OpenAI
OPENAI_API_KEY=your_azure_openai_key
OPENAI_API_BASE=https://your-resource-name.openai.azure.com/
OPENAI_API_VERSION=2024-05-01-preview
OPENAI_DEPLOYMENT_NAME=gpt-35-turbo

# Microsoft Teams Webhook
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...

### 4. Create Microsoft Teams Incoming Webhook

Open your Microsoft Teams channel.
Go to More Options (⋯) → Connectors.
Search for Incoming Webhook and configure it.
Copy the webhook URL and paste it into .env as TEAMS_WEBHOOK_URL.

## 🚀 Usage

### Start the chatbot

python langgraph_bot.py

### Example conversation:
You: Who was the first person to walk on the moon?
Bot: Neil Armstrong, on July 20, 1969, during Apollo 11.

You: send the new tools to the team
Bot: ✅ I've sent the latest AI tools digest to your Microsoft Teams!

## 🛠 How It Works

LangGraph manages the conversation state.
On normal messages → uses Azure OpenAI for chat completion.
On trigger phrase (send the new tools to the team) → calls run_digest() from fetch.py:
Searches SerpAPI for new AI tools (past 7 days).
Downloads and parses each article using newspaper3k.
Summarizes via GPT in structured format.
Sends result to Microsoft Teams webhook.

## 📦 Requirements

Python 3.9+
Azure OpenAI resource with gpt-35-turbo or higher
SerpAPI account (Free or Paid)
Microsoft Teams channel with Incoming Webhook enabled

### Install dependencies:
pip install -r requirements.txt

