# Grammar Fix Desktop App

A simple background application that fixes grammar and spelling of selected text using Google Gemini.

## Setup

1.  **Install Python**: Ensure you have Python 3.7 or higher installed.

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Key**:
    - Copy `.env.example` to `.env`:
      ```bash
      copy .env.example .env
      ```
    - Open `.env` and replace `your_api_key_here` with your actual Google Gemini API key.
    - Get your API key from: https://makersuite.google.com/app/apikey
    
    **Security Note**: Never commit your `.env` file to version control. It's already excluded in `.gitignore`.

## Usage

1.  Run the application:
    ```bash
    python main.py
    ```
2.  The app will run in the background (check your system tray for a green icon).
3.  Select any text in any application.
4.  Press **Ctrl+Shift+1**.
5.  An overlay will appear with the suggested correction.
6.  Click **Fix & Replace** to replace your selected text with the corrected version, or **Dismiss** to ignore.

## Troubleshooting

-   **Hotkey not working?** Try running the script as Administrator, as some apps block key interception.
-   **No overlay?** Check the console output for errors. Ensure you have a valid internet connection and API key.
