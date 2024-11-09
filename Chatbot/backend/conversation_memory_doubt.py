from conversation_memory import get_user_history, update_user_history

MEMORY_FILE_DOUBT = "conversation_memory_doubt.json"

def get_user_history_doubt(user_id):
    """
    Get the conversation history for a specific user for doubts.
    """
    return get_user_history(user_id, memory_file=MEMORY_FILE_DOUBT)

def update_user_history_doubt(user_id, new_entry):
    """
    Update the conversation history for a specific user for doubts.
    """
    return update_user_history(user_id, new_entry, memory_file=MEMORY_FILE_DOUBT)
