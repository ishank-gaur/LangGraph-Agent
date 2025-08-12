# langgraph_bot.py
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing import TypedDict, List
from fetch import run_digest  # Import your existing function

# Load environment variables
load_dotenv()

# Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("OPENAI_API_BASE")
)

# ---- LangGraph State ----
class BotState(TypedDict):
    messages: List[str]

# ---- Nodes ----
def chat_node(state: BotState):
    user_message = state["messages"][-1].lower()

    if "send the new tools to the team" in user_message:
        run_digest(max_tools=5, post_to_teams=True)  # Now actually sends
        reply = "✅ I've sent the latest AI tools digest to your Microsoft Teams!"
    else:
        completion = client.chat.completions.create(
            model=os.getenv("OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": state["messages"][-1]}
            ]
        )
        reply = completion.choices[0].message.content

    return {"messages": state["messages"] + [reply]}

# ---- Build graph ----
graph = StateGraph(BotState)
graph.add_node("chat", chat_node)
graph.set_entry_point("chat")
graph.add_edge("chat", END)

app = graph.compile()

# ---- CLI loop ----
if __name__ == "__main__":
    state = {"messages": []}
    while True:
        user_input = input("You: ")
        state["messages"].append(user_input)
        state = app.invoke(state)
        print("Bot:", state["messages"][-1])
