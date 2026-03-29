import os
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    UnstructuredPowerPointLoader,
    UnstructuredImageLoader,
    UnstructuredFileLoader
)

# A dictionary that maps file extensions to their corresponding loader class.
LOADER_REGISTRY = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".txt": lambda path: TextLoader(path, encoding='utf-8'), # Use lambda for args
    ".pptx": UnstructuredPowerPointLoader,
    ".png": UnstructuredImageLoader,
    ".jpg": UnstructuredImageLoader,
    ".jpeg": UnstructuredImageLoader,
}

def get_loader(file_path):
    """
    Returns the appropriate loader instance for a given file path.
    Falls back to UnstructuredFileLoader for unsupported types.
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    loader_class = LOADER_REGISTRY.get(file_extension)

    if loader_class:
        # Handle loaders that need arguments (like TextLoader)
        if callable(loader_class) and not isinstance(loader_class, type):
            return loader_class(file_path)
        else:
            return loader_class(file_path)
    else:
        # If no specific loader is found, use the general-purpose UnstructuredFileLoader.
        print(f"No specific loader for '{file_extension}'. Falling back to UnstructuredFileLoader.")
        return UnstructuredFileLoader(file_path)
