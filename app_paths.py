"""
Cross-platform app data directory management for Golden-Mouse-RPA
"""
import os
import sys

APP_NAME = "Golden-Mouse-RPA"

def get_app_data_dir():
    """Get the app data directory, creating it if it doesn't exist."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:  # Linux and others
        base = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))

    app_dir = os.path.join(base, APP_NAME)
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

def get_data_path(filename):
    """Get full path for a data file in the app directory."""
    return os.path.join(get_app_data_dir(), filename)

# Convenience functions for common files
def secrets_path():
    return get_data_path("secrets.json")

def status_path():
    return get_data_path("current_status.json")

def payments_csv_path():
    return get_data_path("payments_recorded_by_bot.csv")

def result_table_path():
    return get_data_path("result_table.xlsx")

def uploads_dir():
    """Get the uploads directory, creating it if needed."""
    uploads = os.path.join(get_app_data_dir(), "uploads")
    os.makedirs(uploads, exist_ok=True)
    return uploads

def get_upload_path(filename):
    """Get full path for an uploaded file."""
    return os.path.join(uploads_dir(), filename)

def debug_log_path():
    return get_data_path("debug.log")

def debug_log(message):
    """Write debug message to log file with timestamp - works across processes"""
    from datetime import datetime
    try:
        with open(debug_log_path(), "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")
            f.flush()
            os.fsync(f.fileno())
    except:
        pass
