import os
import sys

try:
    import winreg
except ImportError:  # pragma: no cover - Windows-only feature
    winreg = None


APP_NAME = "GrammarFix"
RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def get_startup_command():
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'

    python_executable = sys.executable
    entry_script = os.path.abspath(sys.argv[0])
    return f'"{python_executable}" "{entry_script}"'


def is_startup_enabled():
    if winreg is None:
        return False

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            return bool(value)
    except FileNotFoundError:
        return False
    except OSError:
        return False


def set_startup_enabled(enabled):
    if winreg is None:
        return False, "Startup settings are only available on Windows."

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY_PATH,
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            if enabled:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, get_startup_command())
                return True, "Grammar Fix will start with Windows."

            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
            return True, "Grammar Fix will stay off until you open it manually."
    except OSError as error:
        return False, f"Could not update startup settings: {error}"
