import os
import time
import shutil
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .core import process_file, PROJECT_ROOT


class NewFileHandler(FileSystemEventHandler):
    """Handles the event when a new file is created in the documents directory."""
    def __init__(self, archive_path, error_path):
        self.archive_path = archive_path
        self.error_path = error_path

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
            destination_path = os.path.join(self.archive_path, filename)
            print(f"Moving processed file to archive: {destination_path}")
            shutil.move(file_path, destination_path)
        else:
            destination_path = os.path.join(self.error_path, filename)
            print(f"Moving failed file to error directory: {destination_path}")
            shutil.move(file_path, destination_path)


def start_watcher(docs_path, archive_path, error_path):
    """Initializes and starts the file system watcher."""
    # Ensure directories exist
    for path in [docs_path, archive_path, error_path]:
        if not os.path.exists(path):
            os.makedirs(path)

    event_handler = NewFileHandler(archive_path, error_path)
    observer = Observer()
    observer.schedule(event_handler, docs_path, recursive=False)

    print(f"Watching for new files in: {os.path.abspath(docs_path)}")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nWatcher stopped by user.")
    observer.join()


if __name__ == "__main__":
    # Define the parent directory of the project root
    parent_dir = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir))

    parser = argparse.ArgumentParser(description="File watcher for the RAG application.")
    parser.add_argument("--docs-path", type=str, default=os.path.join(parent_dir, 'documents'), help="Path to the documents directory.")
    parser.add_argument("--archive-path", type=str, default=os.path.join(parent_dir, 'archive'), help="Path to the archive directory.")
    parser.add_argument("--error-path", type=str, default=os.path.join(parent_dir, 'error'), help="Path to the error directory.")

    args = parser.parse_args()

    start_watcher(args.docs_path, args.archive_path, args.error_path)
