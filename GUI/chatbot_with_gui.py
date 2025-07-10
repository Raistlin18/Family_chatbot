import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from google import genai
from google.genai import types
import threading
import os
import re

class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bell - Personal Assistant")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # API key reading
        try:
            with open("d:/Programming/Projects/APIs/google_AI_api.txt", "r") as file:
                api_key = file.read().strip()
            self.client = genai.Client(api_key=api_key)
        except FileNotFoundError:
            messagebox.showerror("Error", "API key file not found!")
            root.destroy()
            return
        
        # Shopping list file
        self.shoplist_file = "d:/Programming/Projects/family_chatbot/shoplist.txt"
        
        self.setup_ui()
        self.load_shopping_list()
        
    def setup_ui(self):
        # Fő keret
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Grid súlyok
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Bell - Personal Assistant", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 10))
        
        # Chat area
        self.chat_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, 
                                                  height=20, width=80,
                                                  font=('Arial', 10))
        self.chat_area.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(0, 10))
        
        # Message input field
        self.message_entry = ttk.Entry(main_frame, font=('Arial', 10))
        self.message_entry.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        self.message_entry.bind('<Return>', self.send_message)
        
        # Send button
        send_button = ttk.Button(main_frame, text="Send", command=self.send_message)
        send_button.grid(row=2, column=3, padx=(10, 0), pady=(0, 10))
        
        # Shopping list management buttons
        shoplist_frame = ttk.LabelFrame(main_frame, text="Shopping List", padding="5")
        shoplist_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(0, 10))
        
        ttk.Button(shoplist_frame, text="Add Item", command=self.add_item_dialog).grid(row=0, column=0, padx=5)
        ttk.Button(shoplist_frame, text="Remove Item", command=self.remove_item_dialog).grid(row=0, column=1, padx=5)
        ttk.Button(shoplist_frame, text="Show List", command=self.show_shopping_list).grid(row=0, column=2, padx=5)
        ttk.Button(shoplist_frame, text="Exit", command=self.root.quit).grid(row=0, column=3, padx=5)
        
        # Shopping list display
        self.shoplist_display = scrolledtext.ScrolledText(shoplist_frame, wrap=tk.WORD, 
                                                         height=6, width=70,
                                                         font=('Arial', 9))
        self.shoplist_display.grid(row=1, column=0, columnspan=4, pady=(10, 0), sticky="ew")
        
        # Welcome message
        self.add_message("Bell", "Hello! I'm Bell, your patient and helpful family assistant. How can I help you today?")
        
    def add_message(self, sender, message):
        self.chat_area.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_area.see(tk.END)
        
    def send_message(self, event=None):
        message = self.message_entry.get().strip()
        if not message:
            return
            
        # Exit check
        if message.lower() in ["exit", "quit", "bye"]:
            self.add_message("You", message)
            self.add_message("Bell", "Goodbye! 👋")
            self.root.after(2000, self.root.quit)  # Exit after 2 seconds
            return
            
        self.message_entry.delete(0, tk.END)
        self.add_message("You", message)
        
        # AI response generation in separate thread
        threading.Thread(target=self.generate_response, args=(message,), daemon=True).start()
        
    def generate_response(self, message):
        try:
            # Get current shopping list for context
            current_shoplist = self.read_shoplist()
            shoplist_text = "\n".join(current_shoplist) if current_shoplist else "The shopping list is currently empty."
            
            # Augment the prompt with shopping list context
            augmented_prompt = f"""
            You are Bell the patient and helpful family assistant who can answer questions and help with tasks.
            Current shopping list:
            {shoplist_text}

            Based on the user's request, you might need to update the shopping list.
            If the user asks to **add** an item, tell them you've added it and then print the *updated* list.
            If the user asks to **remove** an item, tell them you've removed it and then print the *updated* list.
            If the user asks to **show** the shopping list, just provide the current list.
            For other requests, respond normally.

            User: {message}
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=augmented_prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=1),
                ),
            )
            
            response_text = (response.text or "Sorry, I couldn't respond.").lower()
            
            # Handle shopping list operations based on AI's implied intent
            self.handle_shopping_list_operations(message, response_text, current_shoplist)
            
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            self.root.after(0, lambda: self.add_message("Bell", error_msg))
            
    def handle_shopping_list_operations(self, prompt, response_text, current_shoplist):
        # Add item
        if "add" in response_text or "added" in response_text or "to shoplist" in response_text:
            match = re.search(r"add\s+(.*?)(?:\s+to shopping list|\s+to the list|$)", prompt.lower())
            if match:
                item_to_add = match.group(1).strip()
                
                # Clean up the item name
                for prefix in ["to shopping list", "to the list", "to list", "to shoplist"]:
                    if item_to_add.startswith(prefix):
                        item_to_add = item_to_add[len(prefix):].strip()
                
                if item_to_add and item_to_add.capitalize() not in current_shoplist:
                    current_shoplist.append(item_to_add.capitalize())
                    self.write_shoplist(current_shoplist)
                    
                    output_list = ""
                    if current_shoplist:
                        for i, item in enumerate(current_shoplist, 1):
                            output_list += f"{i}. {item}\n"
                    
                    self.root.after(0, lambda: self.add_message("Bell", f"Okay, I've added '{item_to_add.capitalize()}' to the shopping list. Here's your updated list:\n{output_list.strip()}"))
                    self.load_shopping_list()
                elif item_to_add:
                    self.root.after(0, lambda: self.add_message("Bell", f"'{item_to_add.capitalize()}' is already on the list."))
                else:
                    self.root.after(0, lambda: self.add_message("Bell", "I'm not sure what you wanted to add. Please be more specific."))
            else:
                self.root.after(0, lambda: self.add_message("Bell", "I understood you want to add something, but couldn't parse the item."))
        
        # Remove item
        elif "remove" in response_text and "from shopping list" in response_text:
            match = re.search(r"remove\s+(.*?)(?:\s+from shopping list|\s+from the list|$)", prompt.lower())
            if match:
                item_to_remove = match.group(1).strip()
                if item_to_remove and item_to_remove.capitalize() in current_shoplist:
                    current_shoplist.remove(item_to_remove.capitalize())
                    self.write_shoplist(current_shoplist)
                    self.root.after(0, lambda: self.add_message("Bell", f"Alright, I've removed '{item_to_remove.capitalize()}' from the shopping list. Your updated list is: {', '.join(current_shoplist)}"))
                    self.load_shopping_list()
                elif item_to_remove:
                    self.root.after(0, lambda: self.add_message("Bell", f"'{item_to_remove.capitalize()}' wasn't found on the list. Your current list is: {', '.join(current_shoplist)}"))
                else:
                    self.root.after(0, lambda: self.add_message("Bell", "I'm not sure what you wanted to remove. Please be more specific."))
            else:
                self.root.after(0, lambda: self.add_message("Bell", "I understood you want to remove something, but couldn't parse the item."))
        
        # Show shopping list
        elif "show shopping list" in prompt.lower() or "what's on the list" in prompt.lower() or "list items" in prompt.lower():
            if current_shoplist:
                self.root.after(0, lambda: self.add_message("Bell", f"Here's your current shopping list: {', '.join(current_shoplist)}"))
            else:
                self.root.after(0, lambda: self.add_message("Bell", "Your shopping list is currently empty. 🛒"))
        else:
            # For other responses, just print what Bell says
            self.root.after(0, lambda: self.add_message("Bell", response_text))
            
    def read_shoplist(self, filename=None):
        if filename is None:
            filename = self.shoplist_file
        try:
            with open(filename, "r", encoding='utf-8') as f:
                items = [line.strip() for line in f if line.strip()]
            return items
        except FileNotFoundError:
            return []
            
    def write_shoplist(self, items, filename=None):
        if filename is None:
            filename = self.shoplist_file
        with open(filename, "w", encoding='utf-8') as f:
            for item in items:
                f.write(item + "\n")
                
    def load_shopping_list(self):
        try:
            if os.path.exists(self.shoplist_file):
                with open(self.shoplist_file, "r", encoding='utf-8') as f:
                    items = [line.strip() for line in f if line.strip()]
                self.update_shoplist_display(items)
            else:
                self.update_shoplist_display([])
        except Exception as e:
            self.update_shoplist_display([])
            
    def update_shoplist_display(self, items):
        self.shoplist_display.delete(1.0, tk.END)
        if items:
            for i, item in enumerate(items, 1):
                self.shoplist_display.insert(tk.END, f"{i}. {item}\n")
        else:
            self.shoplist_display.insert(tk.END, "The shopping list is currently empty.")
            
    def add_item_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Item")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Enter the item to add:").pack(pady=10)
        
        entry = ttk.Entry(dialog, width=40)
        entry.pack(pady=10)
        entry.focus()
        
        def add_item():
            item = entry.get().strip()
            if item:
                try:
                    current_items = self.read_shoplist()
                    if item.capitalize() not in current_items:
                        current_items.append(item.capitalize())
                        self.write_shoplist(current_items)
                        self.load_shopping_list()
                        self.add_message("Bell", f"'{item.capitalize()}' added to the shopping list.")
                        dialog.destroy()
                    else:
                        messagebox.showwarning("Warning", "This item is already on the list!")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not add item: {str(e)}")
            else:
                messagebox.showwarning("Warning", "Please enter an item!")
                
        ttk.Button(dialog, text="Add", command=add_item).pack(pady=10)
        entry.bind('<Return>', lambda e: add_item())
        
    def remove_item_dialog(self):
        try:
            items = self.read_shoplist()
            
            if not items:
                messagebox.showinfo("Info", "The shopping list is empty.")
                return
                
            dialog = tk.Toplevel(self.root)
            dialog.title("Remove Item")
            dialog.geometry("400x300")
            dialog.transient(self.root)
            dialog.grab_set()
            
            ttk.Label(dialog, text="Select the item to remove:").pack(pady=10)
            
            listbox = tk.Listbox(dialog, height=10)
            listbox.pack(pady=10, fill=tk.BOTH, expand=True)
            
            for item in items:
                listbox.insert(tk.END, item)
                
            def remove_item():
                selection = listbox.curselection()
                if selection:
                    item_to_remove = items[selection[0]]
                    try:
                        items.remove(item_to_remove)
                        self.write_shoplist(items)
                        self.load_shopping_list()
                        self.add_message("Bell", f"'{item_to_remove}' removed from the shopping list.")
                        dialog.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not remove item: {str(e)}")
                else:
                    messagebox.showwarning("Warning", "Please select an item!")
                    
            ttk.Button(dialog, text="Remove", command=remove_item).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load the list: {str(e)}")
            
    def show_shopping_list(self):
        try:
            items = self.read_shoplist()
            
            if items:
                list_text = "Shopping List:\n" + "\n".join(f"{i}. {item}" for i, item in enumerate(items, 1))
                self.add_message("Bell", list_text)
            else:
                self.add_message("Bell", "Your shopping list is empty.")
        except Exception as e:
            self.add_message("Bell", f"Error loading the list: {str(e)}")

def main():
    root = tk.Tk()
    app = ChatbotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
