import os 
import pdfplumber
import base64
from PIL import Image
import io
from utils.logger import logger

def detect_file_type(uploaded_file):
    """
    Checks the uploaded file extension and returns
    either 'pdf' or 'image' so we know how to process it.
    """
    filename = uploaded_file.name.lower()
    if filename.endswith(".pdf"):
        return "pdf"
    elif filename.endswith((".png", ".jpg", ".jpeg", ".webp")):
        return "image"
    elif filename.endswith(".doc", ".docx"):
        return "document"
    elif filename.endswith(".md"):
        return "markdown"
    else:
        return "unsupported"

def table_to_markdown(table:list):
    """
    Converts a pdfplumber table (list of lists) into a markdown table string.
    First row is treated as the header. Empty cells are replaced with empty string to avoid None errors.
    """
    if not table or len(table)<2:
        return ""
    cleaned = []
    for row in table:
        cleaned_row = [cell if cell is not None else "" for cell in row]
        cleaned.append(cleaned_row)
    header = cleaned[0]
    rows = cleaned[1:]

    md =  "| " + " | ".join(header)+ "|\n"
    md += "| " + " | ".join(["---"] * len(header)) + " |\n"
    for row in rows:
        md+= "| "+" | ".join(row)+"|\n"
    return md


def extract_from_pdf(uploaded_file):
    """
    Opens a PDF using pdfplumber, page by page.
        - Tables → converted to markdown using table_to_markdown()
        - Plain text → added as-is
    Returns one clean markdown string combining all pages.
    """
    extracted_content = []
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page_num , page in enumerate(pdf.pages, start=1):
                extracted_content.append(f"\n-- Page {page_num}--\n")
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        md_table = table_to_markdown(table)
                        if md_table:
                            extracted_content.append(md_table)
                text = page.extract_text()
                if text:
                    extracted_content.append(text.strip())
        return "\n".join(extracted_content)
    except Exception as e:
        logger.error(f"Error extracting PDF: {str(e)}")
        return f"Error processing PDF: {str(e)}"

def extract_from_image(uploaded_file):
    """
    Reads the uploaded image and converts it to a base64 string. This base64 string gets sent directly to the Groq vision model
    in Phase 3 — we don't do OCR ourselves.
    Returns: (base64_string, media_type)
    """
    try:
        filename = uploaded_file.name.lower()
        uploaded_file.seek(0)
        file_bytes = uploaded_file.read()
        if filename.endswith(".png"):
            media_type = "image/png"
        elif filename.endswith((".jpg", ".jpeg")):
            media_type = "image/jpeg"
        elif filename.endswith(".webp"):
            media_type = "image/webp"
        else:
            media_type = "image/png"

        base64_string = base64.b64encode(image_bytes).decode("utf-8")

        return base64_string, media_type
    except:
        logger.error(f"Error encoding image: {str(e)}")
        return None, None



if __name__ == "__main__":
    sample_table = [
        ["Date", "Description", "Amount", "Balance"],
        ["12/02/2026", "Payment", "$300.00", "$5,660.00"],
        ["12/02/2026", "Amazon Web Services EC2 Usage", "$320.45", "$4,512.78"],
    ]
    print(table_to_markdown(sample_table))

