from groq import Groq
from utils.logger import logger
from dotenv import load_dotenv
import os
from utils.logger import logger
load_dotenv()

VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

VISION_PROMPT = """
You are a financial document parser. Carefully analyze this image 
of a financial document (credit card statement, invoice, receipt, 
or expense report).

Extract ALL information you can see and return it in this exact format:

## Document Type
[What type of document is this?]

## Key Details
- Statement Date: [date if visible]
- Account Number: [last 4 digits only, mask the rest as XXXX]
- Due Date: [if visible]

## Transactions Table
Convert ALL visible transactions into a markdown table:
| Date | Description | Amount | Balance |
|------|-------------|--------|---------|
[fill all rows]

## Summary Section
Extract all summary lines exactly as shown:
- Previous Balance: $X
- Payments Received: $X  
- New Charges: $X
- Taxes & Fees: $X
- Total Due: $X

## Visual Cues
Note any important visual information:
- Highlighted rows (which ones and why they seem highlighted)
- Any text marked as PENDING or flagged
- Any unusual formatting or warnings

Return ONLY the structured data above. No extra commentary.
"""


def analyze_image(base64_string:str,media_type:str)->str:
    """
    Sends a base64 encoded image to Groq's vision model.
    Returns structured markdown text describing all financial
    data visible in the image.

    base64_string : from extract_from_image() in Phase 1
    media_type    : "image/png", "image/jpeg" etc.
    """
    try:
        logger.info("Sending image to Groq vision model")
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
               model=VISION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{base64_string}"
                                }
                            },
                            {
                                "type": "text",
                                "text": VISION_PROMPT
                            }
                        ]
                    }
                ],
                temperature=0.1,    
                max_tokens=2048     
        )
        if response.choices:
            extracted_text = response.choices[0].message.content
        else:
            extracted_text = "No content returned from vision model."
        logger.info("Vision model extraction successful")
        return extracted_text

    except Exception as e:
        logger.error(f"Vision model error: {str(e)}", exc_info=True)
        return f"Error analyzing image: {str(e)}"
    

def merge_contexts(vision_output: str, pdf_output: str = "") -> str:
    """
    Merges vision model output with any PDF extracted text.
    
    In most cases only one will exist:
      - Image upload  → vision_output only
      - PDF upload    → pdf_output only
      - Both          → merged with clear labels
    
    Returns single string passed to build_agent() in Phase 2.
    """
    if not pdf_output.strip():
        return vision_output
    if not vision_output.strip():
        return pdf_output
    
    merged  =f"""
                ## Extracted from Document (PDF)
                {pdf_output}
                ## Extracted from Image (Vision Model)
            {vision_output}
            """
    logger.info("Merged PDF and vision contexts")
    return merged.strip()

        

