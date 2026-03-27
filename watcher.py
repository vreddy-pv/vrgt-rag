
import os
import time
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core import process_file

# Define paths
DOCUMENTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'documents')
ARCHIVE_PATH = os.path.join(os.path.dirname(__file__), '..', 'archive')
ERROR_PATH = os.path.join(os.path.dirname(__file__), '..', 'error')

class NewFileHandler(FileSystemEventHandler):
    """Handles the event when a new file is created in the documents directory."""
    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        filename = os.path.basename(file_path)
        print(f"\nNew file detected: {filename}")

        # Wait a moment to ensure the file is fully written
        time.sleep(1)

        # Process the file using the core logic
        success = process_file(file_path)

        # Move the file to the appropriate directory
        if success:
            destination_path = os.path.join(ARCHIVE_PATH, filename)
            print(f"Moving processed file to archive: {destination_path}")
            shutil.move(file_path, destination_path)
        else:
            destination_path = os.path.join(ERROR_PATH, filename)
            print(f"Moving failed file to error directory: {destination_path}")
            shutil.move(file_path, destination_path)

def start_watcher():
    """Initializes and starts the file system watcher."""
    # Ensure directories exist
    for path in [DOCUMENTS_PATH, ARCHIVE_PATH, ERROR_PATH]:
        if not os.path.exists(path):
            os.makedirs(path)

    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, DOCUMENTS_PATH, recursive=False)

    print(f"Watching for new files in: {os.path.abspath(DOCUMENTS_PATH)}")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nWatcher stopped by user.")
    observer.join()

if __name__ == "__main__":
    start_watcher()
