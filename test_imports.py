try:
    import google.generativeai
    import pyperclip
    import keyboard
    from PyQt6.QtWidgets import QApplication
    print("Imports successful")
except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
