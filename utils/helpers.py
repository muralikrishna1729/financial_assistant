import os
import re
from utils.logger import logger


SUPPORTED_TYPES = [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".md", ".doc",".docx"]
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

def validate_uploaded_file(uploaded_file):
    """
    Validates the file for size and type to protect the app's memory.
    Returns: (is_valid, error_message)
    """
    if uploaded_file is None:
        return False, "No file uploaded."
    
    filename = uploaded_file.name.lower()
    is_supported = any(filename.endswith(ext) for ext in SUPPORTED_TYPES)
    if not is_supported:
        return False, f"Unsupported file type. Please upload: {', '.join(SUPPORTED_TYPES)}"
    
    if uploaded_file.size > MAX_FILE_SIZE_BYTES:
        readable_size = format_file_size(uploaded_file.size)
        return False, f"File too large ({readable_size}). Maximum allowed size is {MAX_FILE_SIZE_MB}MB."

    return True, ""

def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        size_kb = size_bytes / 1024
        return f"{size_kb:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        size_mb = size_bytes / (1024 * 1024)
        return f"{size_mb:.1f} MB"
    else:
        size_gb = size_bytes / (1024 * 1024 * 1024)
        return f"{size_gb:.1f} GB"
    
def clean_extracted_text(text):
    """
    Cleans up raw extracted text from pdfplumber.
    Removes:
      - Non-breaking spaces (\xa0) common in PDFs
      - More than 2 consecutive blank lines
      - Lines that are only dashes or underscores (visual separators)
      - Leading/trailing whitespace from each line
    
    Returns cleaned text string.
    """
    if not text or not text.strip():
        return ""
    text = text.replace("\xa0","")
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if re.match(r'^[-_=]{3,}$', stripped):
            continue
        cleaned_lines.append(stripped)
    
    cleaned_text = "\n".join(cleaned_lines)
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    return cleaned_text.strip()

