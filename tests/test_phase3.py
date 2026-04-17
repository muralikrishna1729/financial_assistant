import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.vision import analyze_image, merge_contexts
from core.extractor import extract_from_image


# ─────────────────────────────────────────────
# Test 1: merge_contexts logic (no API needed)
# ─────────────────────────────────────────────
print("=" * 50)
print("TEST 1: merge_contexts")
print("=" * 50)

# Case 1: image only
result = merge_contexts("Vision output here", "")
print("Image only:")
print(result)

# Case 2: pdf only
result = merge_contexts("", "PDF output here")
print("\nPDF only:")
print(result)

# Case 3: both
result = merge_contexts("Vision output here", "PDF output here")
print("\nBoth merged:")
print(result)


# ─────────────────────────────────────────────
# Test 2: Real image → vision model
# ─────────────────────────────────────────────
print("\n" + "=" * 50)
print("TEST 2: Vision model with real image")
print("=" * 50)

image_path = "33.jpg"  # save the screenshot here

if Path(image_path).exists():

    # Simulate Streamlit uploaded file
    class FakeUploadedFile:
        def __init__(self, path):
            self.name = Path(path).name
            self.size = Path(path).stat().st_size
            self._path = path

        def read(self):
            return open(self._path, "rb").read()

    fake_file = FakeUploadedFile(image_path)

    # Step 1: Convert to base64
    base64_str, media_type = extract_from_image(fake_file)
    print(f"Image converted to base64. Media type: {media_type}")
    print(f"Base64 length: {len(base64_str)} characters")

    # Step 2: Send to vision model
    print("\nSending to Groq vision model...")
    result = analyze_image(base64_str, media_type)

    print("\n--- Vision Model Output ---")
    print(result)

else:
    print(f"No image found at '{image_path}'")
    print("Save the credit card screenshot as 'sample_statement.png' in root folder")