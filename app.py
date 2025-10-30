# app.py
import chainlit as cl
from restaurant_assistant import build_agent
import re

CSV_PATH = "./data/store-summary-data.csv"

def split_freeform(text: str):
    # simple splitter for multi-intent messages
    parts = re.split(r"[?;\n]+", text)
    return [p.strip() for p in parts if p.strip()]

@cl.on_chat_start
def start():
    agent = build_agent(CSV_PATH)
    cl.user_session.set("agent", agent)
    cl.Message(content="Restaurant data loaded. Ask me anything about it.").send()

@cl.on_message
async def main(message: cl.Message):
    agent = cl.user_session.get("agent")
    user_text = message.content

    # try full message first
    try:
        full = agent.invoke({"input": user_text})
        await cl.Message(content=full["output"]).send()
        return
    except Exception:
        # if it fails (too many asks at once), fall back to splitting
        pass

    # fallback: split into atomic questions
    subqs = split_freeform(user_text)
    outputs = []
    for q in subqs:
        try:
            res = agent.invoke({"input": q})
            outputs.append(f"**{q}**\n{res['output']}")
        except Exception as e:
            outputs.append(f"**{q}**\nError: {e}")

    await cl.Message(content="\n\n---\n\n".join(outputs)).send()
