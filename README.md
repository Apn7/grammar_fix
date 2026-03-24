# Grammar Fix Desktop App

Grammar Fix is a desktop background application that corrects grammar and spelling for selected text using AI providers (Groq and Google Generative AI). It runs in the system tray, listens for a global hotkey, and shows an overlay to apply corrections instantly.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Codebase Index](#codebase-index)
- [Operational Notes](#operational-notes)
- [Troubleshooting](#troubleshooting)
- [Security](#security)

## Features

- Four global hotkey workflows:
  - **Ctrl+Shift+1**: Grammar fix
  - **Ctrl+Shift+2**: English ↔ Bengali translation
  - **Ctrl+Shift+3**: Code explanation
  - **Ctrl+Shift+4**: Smart text help (auto-select summary or explanation)
- Smart mode behavior:
  - Longer input is summarized
  - Shorter input is explained
- System tray background operation with quick actions for all workflows
- Overlay-based result review before replacing/copied output
- Provider abstraction for Groq and Google Gemini backends
- Runtime provider/model switching from Control Center
- Persistent settings for provider/model preferences
- Optional **Start With Windows** support (Windows)

## Requirements

- Python 3.7+
- Desktop environment with clipboard access
- Internet access for API calls
- Windows is the primary supported platform (global hotkey behavior may require elevated privileges)

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create environment file:
   - macOS/Linux:
     ```bash
     cp .env.example .env
     ```
   - Windows:
     ```bat
     copy .env.example .env
     ```
3. Update `.env` with your provider keys.
4. Start the app:
   ```bash
   python main.py
   ```

## Configuration

Environment variables are loaded from `.env`:

- `GROQ_API_KEY`: API key for Groq (https://console.groq.com/keys)
- `GEMINI_API_KEY`: API key for Google Generative AI (if using Gemini)

Provider/model runtime selection is managed by the Control Center and persisted by `settings_manager.py`.

## Usage

1. Launch the app with `python main.py`.
2. Keep it running in the system tray.
3. Select text in any application.
4. Use one of the global shortcuts:
   - **Ctrl+Shift+1**: Grammar fix
   - **Ctrl+Shift+2**: Translation
   - **Ctrl+Shift+3**: Code explanation
   - **Ctrl+Shift+4**: Smart summarize/explain
5. Review the result in the overlay.
6. Use the available action:
   - **Replace Selection** for correction/translation flows
   - **Copy** action for explanation/summary flows
   - **Close** to dismiss without changes

## Codebase Index

| File | Responsibility |
| --- | --- |
| `main.py` | Entry point, application lifecycle, hotkey orchestration, and workflow coordination |
| `overlay.py` | Correction overlay UI and user interaction handling |
| `control_center.py` | Main control UI for provider/model selection and app controls |
| `provider_manager.py` | Unified provider routing and correction request dispatch |
| `groq_client.py` | Groq API integration and response parsing |
| `gemini_client.py` | Google Generative AI integration |
| `settings_manager.py` | Persistent settings read/write |
| `startup_manager.py` | Startup behavior integration |
| `clipboard_utils.py` | Clipboard access and helper operations |
| `config.py` | Shared constants/configuration values |
| `test_imports.py` | Basic dependency/import smoke-check script |
| `requirements.txt` | Runtime dependency list |
| `.env.example` | Template for required environment variables |
| `SECURITY_IMPROVEMENTS.md` | Security-focused implementation notes |

## Operational Notes

- The app runs as a background process and is controlled from the system tray icon.
- Hotkey interception can be blocked by privileged applications; running with elevated permissions may be required on Windows.
- Provider/model availability depends on valid API credentials and network connectivity.
- You can open Control Center from the tray to switch providers/models or toggle **Start With Windows**.

## Troubleshooting

- **Hotkey not working**: Run as Administrator (Windows) and confirm no other app is consuming the same shortcut.
- **No correction result**: Verify API key(s), internet connectivity, and provider selection in Control Center.
- **Import errors**: Reinstall dependencies with `pip install -r requirements.txt` in the active Python environment.

## Security

- Never commit `.env` or API keys.
- Review `SECURITY_IMPROVEMENTS.md` for implemented safeguards and recommended operating practices.
