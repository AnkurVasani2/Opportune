import json
import os

MEMORY_FILE = "conversation_memory.json"

def load_conversation_history():
    """
    Load the conversation history from a JSON file if it exists.
    """
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_conversation_history(conversation_history):
    """
    Save the conversation history to a JSON file.
    """
    with open(MEMORY_FILE, 'w') as file:
        json.dump(conversation_history, file)

def get_user_history(user_id):
    """
    Get the conversation history for a specific user.
    """
    history = load_conversation_history()
    return history.get(user_id, [])

def update_user_history(user_id, new_entry):
    """
    Update the conversation history for a specific user.
    """
    history = load_conversation_history()
    if user_id not in history:
        history[user_id] = []
    history[user_id].append(new_entry)
    save_conversation_history(history)
