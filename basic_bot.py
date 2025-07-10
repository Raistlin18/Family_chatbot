from google import genai
from google.genai import types
import re

# kulcs beolvasása fileból
with open("d:/Programming/Projects/APIs/google_AI_api.txt", "r") as file:
    api_key = file.read()

client = genai.Client(api_key=api_key)

while True:
    # prompt bekérése
    prompt = input("\nEnter your prompt (or 'bye' to quit): ")

    if prompt.lower() in ["exit", "quit", "bye"]:
        print("Goodbye! 👋")
        break

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=1), # thinking_budget: 0 = no thinking, 1 = thinking
            system_instruction="You are Bell the patient and helpful family assistant who can answer questions and help with tasks."
        ),
    )

    print("\nBell: ", response.text, "\n")


