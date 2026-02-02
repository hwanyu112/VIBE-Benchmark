import os
from openai import OpenAI


def make_client() -> OpenAI:
    api_key = os.environ["OPENAI_API_KEY"]
    return OpenAI(api_key=api_key)

def get_model_name() -> str:
    return os.environ.get("OPENAI_MODEL", "gpt-5.1_2025-11-13")
