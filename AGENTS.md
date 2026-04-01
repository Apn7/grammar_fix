# AGENTS.md — GrammarFix

This file provides system instructions for agentic coding assistants (e.g., Cursor, Copilot) operating in the GrammarFix repository. It outlines project commands, architecture, and strict coding conventions.

*(Note: No `.cursorrules` or `.github/copilot-instructions.md` exist in this repository. These guidelines serve as the unified source of truth for agent behavior.)*

---

## 1. Build, Lint, and Test Commands

### Environment Setup & Running
GrammarFix requires Windows for full functionality (uses `winreg`, global keyboard hooks, system tray).
```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

### Build (Standalone EXE)
```bash
pip install pyinstaller
pyinstaller GrammarFix.spec
# Output: dist/GrammarFix.exe
```

### Testing (Important for Agents)
There is no formal test framework yet, but there is one smoke-test file. **When adding real tests or verifying logic, always use `pytest`.** 

**Commands to run tests:**
```bash
# Run the existing import smoke test
python test_imports.py

# RUN A SINGLE TEST FILE
pytest test_imports.py

# RUN A SINGLE TEST FUNCTION (Crucial for isolated testing)
pytest test_imports.py::test_function_name

# RUN TESTS MATCHING A KEYWORD
pytest -k "keyword"
```

### Linting & Formatting
No lint configuration file exists. Run style checks manually using `ruff`:
```bash
ruff check .                   # Run linter
ruff format --check .          # Check formatting without modifying
ruff format .                  # Auto-format codebase
```

---

## 2. Code Style & Architecture Guidelines

### Python Version & Core Formatting
- **Version**: Target Python 3.10+. The codebase compiles under CPython 3.13. Do not use features unavailable before 3.10.
- **Indentation**: 4 spaces strictly. No tabs.
- **Quotes**: Double quotes for all strings (to remain consistent with existing code).
- **Line Length**: Maximum 100 characters (PyQt6 stylesheet strings are exempt).
- **Trailing Commas**: Use trailing commas in multi-line collections and argument lists.

### Imports
- **Order**: Standard library imports first, then third-party, then local. Separate each group by a single blank line.
- **Wildcards**: No wildcard imports (`from x import *`).
- **Local Imports**: Use plain module names, never relative dots.
  ```python
  # CORRECT
  from config import VERTEX_AI_API_KEY
  from clipboard_utils import get_selected_text

  # WRONG
  from .config import VERTEX_AI_API_KEY
  ```

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `GroqClient`, `OverlayWindow`, `ProviderManager`)
- **Functions / Methods**: `snake_case` (e.g., `fix_grammar`, `get_selected_text`)
- **Constants / Module-level**: `UPPER_SNAKE_CASE` (e.g., `VERTEX_AI_API_KEY`, `APP_NAME`)
- **Private Helpers**: Single leading underscore (e.g., `_make_request`, `_fetch_groq_models`)
- **Qt Signal Names**: `snake_case` pyqtSignal attributes (e.g., `show_loading`)
- **Widget Object Names** (`setObjectName`): `camelCase` strings matching the QSS selectors exactly.

### Type Hints
- Add type hints to **all new public functions** and method signatures.
- Use `str | None` union syntax (Python 3.10+), not `Optional[str]`.
- Return types are required on all functions except `__init__`.
  ```python
  def fix_grammar(self, text: str) -> str | None:
  ```

### Error Handling (Critical)
- **Specificity**: Catch the most specific exception available; avoid bare `except:`.
- **Network Calls**: APIs (`requests`) must catch their own library exceptions and return `None` on failure. **Never propagate network errors to the Qt main thread directly.** Print a descriptive message to stdout instead.
- **API Keys**: `ValueError` is the canonical signal that an API key is missing or invalid. Functions like `ProviderManager.get_client` will raise this, and callers must catch it to show a user-facing error message. Do not swallow it silently.
- **OS Modules**: Windows-only modules (`winreg`) must be guarded with a `try/except ImportError` at the module level.

### PyQt6 & GUI Patterns
- **Threading Restrictions**: Never call Qt UI methods from a background thread. All cross-thread communication must go through `pyqtSignal` / `emit()` (see `WorkerSignals` in `main.py`).
- **Background Tasks**: Background work runs in `threading.Thread(daemon=True)`. Do not use `QThread` unless the task requires tight Qt integration.
- **Stylesheets**: Stylesheet strings live inline in `init_ui` methods. Do not move styles to external `.qss` files without updating the PyInstaller build spec.
- **Widget Names**: Widget object names must match QSS selectors exactly.

### AI Client Interface Structure
Both `GroqClient` and `VertexClient` implement the exact same five methods. Any new AI provider client **must** implement all five with identical signatures:
```python
def fix_grammar(self, text: str) -> str | None: ...
def translate_text(self, text: str) -> str | None: ...
def explain_code(self, text: str) -> str | None: ...
def summarize_text(self, text: str) -> str | None: ...
def explain_text(self, text: str) -> str | None: ...
```

### Security & State Management
- **Settings**: User preferences are stored in `user_settings.json` (git-ignored). Always read/write through `settings_manager.py`. `DEFAULT_SETTINGS` is the authoritative fallback.
- **Secrets**: Never hardcode API keys. Read from `.env` via `config.py`. Do not log or print API keys.
