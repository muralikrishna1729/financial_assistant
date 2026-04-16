import sys
from pathlib import Path

# Make sure Python finds our core/ and utils/ modules
sys.path.append(str(Path(__file__).parent))

from utils.helpers import validate_uploaded_file, format_file_size, clean_extracted_text
from core.extractor import detect_file_type, extract_from_pdf, table_to_markdown


# ─────────────────────────────────────────────
# Test 1: table_to_markdown (no file needed)
# ─────────────────────────────────────────────
print("=" * 50)
print("TEST 1: table_to_markdown")
print("=" * 50)

sample_table = [
    ["Date", "Description", "Amount", "Balance"],
    ["12/02/2026", "Payment", "$300.00", "$5,660.00"],
    ["12/02/2026", "Amazon Web Services EC2 Usage", "$320.45", "$4,512.78"],
    ["12/02/2026", None, "$15.99", None],   # test None handling
]

result = table_to_markdown(sample_table)
print(result)


# ─────────────────────────────────────────────
# Test 2: clean_extracted_text
# ─────────────────────────────────────────────
print("=" * 50)
print("TEST 2: clean_extracted_text")
print("=" * 50)

messy_text = """
  Credit Card Statement  

--------------------

Previous Balance:\xa0$4,215.60

Payments Received: -$600.00



Total Due: $4,512.78

__________
"""

cleaned = clean_extracted_text(messy_text)
print(repr(cleaned))  # repr shows \n explicitly so we can verify cleanup


# ─────────────────────────────────────────────
# Test 3: format_file_size
# ─────────────────────────────────────────────
print("=" * 50)
print("TEST 3: format_file_size")
print("=" * 50)

print(format_file_size(500))           # expected: 500 B
print(format_file_size(15000))         # expected: 14.6 KB
print(format_file_size(2457600))       # expected: 2.3 MB


# ─────────────────────────────────────────────
# Test 4: PDF extraction (only runs if you have a PDF)
# ─────────────────────────────────────────────
print("=" * 50)
print("TEST 4: PDF extraction")
print("=" * 50)

pdf_path = "sample_statement.pdf"   # put any PDF in root folder

if Path(pdf_path).exists():
    # Simulate what Streamlit's uploaded_file gives us
    class FakeUploadedFile:
        def __init__(self, path):
            self.name = Path(path).name
            self.size = Path(path).stat().st_size
            self._path = path

        def read(self):
            return open(self._path, "rb").read()

    fake_file = FakeUploadedFile(pdf_path)

    # Test validation
    is_valid, error = validate_uploaded_file(fake_file)
    print(f"Validation: valid={is_valid}, error='{error}'")

    # Test extraction
    if is_valid:
        raw_text = extract_from_pdf(fake_file)
        cleaned_text = clean_extracted_text(raw_text)
        print("\n--- Extracted & Cleaned Output ---")
        print(cleaned_text[:1000])  # print first 1000 chars only
        print(f"\n... Total length: {len(cleaned_text)} characters")
else:
    print(f"No PDF found at '{pdf_path}' — skipping Test 4.")
    print("Drop any bank statement PDF in the root folder and rename it sample_statement.pdf")