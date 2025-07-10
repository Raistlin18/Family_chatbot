from google import genai
from google.genai import types
from functions import read_shoplist, write_shoplist, remove_item

# read api key from file
with open("d:/Programming/Projects/APIs/google_AI_api.txt", "r") as file:
    api_key = file.read()

client = genai.Client(api_key=api_key)

user_name = input("Please enter your name: ")

print(f"Bell: Hello, {user_name}! I'm Bell, your personal assistant. How can I help you today?")
print("\tIf you want to manage the shopping list, please type 'manage shoplist'.")
print("\tIf you want to exit, please type 'exit', 'quit', or 'bye'.")

while True:
    # request prompt
    prompt = input(f"\n{user_name}: ")

    if "exit" or "quit" or "bye" in prompt.lower():
        print(f"Bell: Goodbye, {user_name}! 👋")
        break

    if "manage shoplist" in prompt.lower():
        shoplist_management = True
        
        while shoplist_management:
            
                print("Bell: What would you like to do with the shopping list?\n\nType 'add' to add an item, 'remove' to remove an item, 'show' to show the shopping list, or 'back' to go back to the chat.")
                prompt = input(f"{user_name}: ")
                
                if "add" in prompt:
                    print("Bell: Please enter the item you want to add to the shopping list, separated by commas.")
                    item = [input(f"{user_name}: ").split(",")]
                    print(item)
                    for i in item:
                        write_shoplist(i)
                    print("Bell: Item added to the shopping list.")
                    continue
                if "remove" in prompt:
                    print("Bell: Please enter the item you want to remove from the shopping list, separated by commas.")
                    item = input(f"{user_name}: ").split(",")
                    print(item)
                    for i in item:
                        remove_item(i)
                    print("Bell: Item removed from the shopping list.")
                    continue
                if "show" in prompt:
                    current_shoplist = read_shoplist()
                    shoplist_text = "\n".join(current_shoplist) if current_shoplist else "\nThe shopping list is currently empty."
                    print(f"Bell: Here is your shopping list: \n{shoplist_text}\n")
                    continue
                if "back" in prompt:
                    shoplist_management = False

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=1), # thinking_budget: 0 = no thinking, 1 = thinking
            system_instruction="You are Bell the patient and helpful family assistant who can answer questions and help with tasks."
        ),
    )

    print("\nBell: ", response.text, "\n")


