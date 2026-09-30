import os
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    model = os.getenv("MODEL_NAME")

    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(model=model or "llama-3.3-70b-versatile", temperature=0)

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=model or "gemini-3.8-flash", temperature=0)

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=model or "qwen2.5:7b", temperature=0)

    raise ValueError(f"Unknown LLM_PROVIDER: {provider}")