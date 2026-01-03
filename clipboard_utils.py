import pyperclip
import time
import keyboard

def get_selected_text():
    # Clear clipboard first to ensure we get new selection
    original_clipboard = pyperclip.paste()
    pyperclip.copy("") 
    
    # Simulate Ctrl+C to copy selected text
    # We add a small delay to ensure the system is ready
    time.sleep(0.1)
    keyboard.send('ctrl+c')
    time.sleep(0.3) # Wait for clipboard to update (increased from 0.1)
    
    selected_text = pyperclip.paste()
    
    # Restore original clipboard if nothing was selected (optional, but good for UX)
    # For this simple app, we might just want to return what we got.
    # If selected_text is empty, it means nothing was selected.
    
    if not selected_text:
        pyperclip.copy(original_clipboard)
        return None
        
    return selected_text

def replace_selected_text(new_text):
    pyperclip.copy(new_text)
    time.sleep(0.3) # Wait for focus to return to original window
    keyboard.send('ctrl+v')
