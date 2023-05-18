import os
import os.path
from typing import Generator, List
from Commands import Commands
from Config import Config

CFG = Config()
WORKING_DIRECTORY = CFG.WORKING_DIRECTORY
LOG_FILE = "file_logger.txt"
LOG_FILE_PATH = os.path.join(WORKING_DIRECTORY, LOG_FILE)
WORKING_DIRECTORY = str(WORKING_DIRECTORY)
if not os.path.exists(WORKING_DIRECTORY):
    os.makedirs(WORKING_DIRECTORY)


class file_operations(Commands):
    def __init__(self):
        self.commands = {
            "Check Duplicate Operation": self.check_duplicate_operation,
            "Read File": self.read_file,
            "Write to File": self.write_to_file,
            "Append to File": self.append_to_file,
            "Delete File": self.delete_file,
            "Search Files": self.search_files,
        }

    @staticmethod
    def check_duplicate_operation(operation: str, filename: str) -> bool:
        log_content = file_operations.read_file(LOG_FILE)
        log_entry = f"{operation}: {filename}\n"
        return log_entry in log_content

    @staticmethod
    def safe_join(base: str, paths) -> str:
        if "/path/to/" in paths:
            paths = paths.replace("/path/to/", "")
        if str(CFG.WORKING_DIRECTORY_RESTRICTED).lower() == "true":
            new_path = os.path.normpath(os.path.join(base, *paths.split("/")))
            if not os.path.exists(new_path):
                os.makedirs(new_path)
        else:
            new_path = os.path.normpath(os.path.join("/", *paths))
            if not os.path.exists(new_path):
                os.makedirs(new_path)
        return new_path

    @staticmethod
    def split_file(
        content: str, max_length: int = 4000, overlap: int = 0
    ) -> Generator[str, None, None]:
        start = 0
        content_length = len(content)

        while start < content_length:
            end = start + max_length
            if end + overlap < content_length:
                chunk = content[start : end + overlap]
            else:
                chunk = content[start:content_length]
            yield chunk
            start += max_length - overlap

    @staticmethod
    def read_file(filename: str) -> str:
        try:
            filepath = file_operations.safe_join(WORKING_DIRECTORY, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            return content
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def write_to_file(filename: str, text: str) -> str:
        if file_operations.check_duplicate_operation("write", filename):
            return "Error: File has already been updated."
        try:
            filepath = file_operations.safe_join(WORKING_DIRECTORY, filename)
            directory = os.path.dirname(filepath)
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)
            return "File written to successfully."
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def append_to_file(filename: str, text: str) -> str:
        try:
            filepath = file_operations.safe_join(WORKING_DIRECTORY, filename)
            with open(filepath, "a") as f:
                f.write(text)
            return "Text appended successfully."
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def delete_file(filename: str) -> str:
        if file_operations.check_duplicate_operation("delete", filename):
            return "Error: File has already been deleted."
        try:
            filepath = file_operations.safe_join(WORKING_DIRECTORY, filename)
            os.remove(filepath)
            return "File deleted successfully."
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def search_files(directory: str) -> List[str]:
        found_files = []

        if directory in {"", "/"}:
            search_directory = WORKING_DIRECTORY
        else:
            search_directory = file_operations.safe_join(WORKING_DIRECTORY, directory)

        for root, _, files in os.walk(search_directory):
            for file in files:
                if file.startswith("."):
                    continue
                relative_path = os.path.relpath(
                    os.path.join(root, file), WORKING_DIRECTORY
                )
                found_files.append(relative_path)

        return found_files
