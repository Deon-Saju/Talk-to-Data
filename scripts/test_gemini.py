import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
llm = ChatGoogleGenerativeAI(model=os.getenv("MODEL_NAME", "gemini-3.8-flash"))

def text_of(content):
    if isinstance(content, list):
        return "".join(p.get("text", "") for p in content
                       if isinstance(p, dict) and p.get("type") == "text")
    return content

reply = llm.invoke("Say hello in one sentence.")
print(text_of(reply.content))