import base64
import json
import re
from groq import Groq
from pydantic import BaseModel, Field

class InvoiceData(BaseModel):
    invoice_number: str = Field(default="N/A")
    invoice_date: str = Field(default="N/A")
    total_amount: float = Field(default=0.0)
    vendor: str = Field(default="Unknown")

def extract_text_from_image(image_bytes):
    client = Groq()
    
    # Encode image to Base64
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    image_data_url = f"data:image/png;base64,{image_b64}"

    # 1. Vision OCR: Extract raw text from the image
    vision_completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": [
            {"type": "text", "text": "Extract all text from this image accurately."},
            {"type": "image_url", "image_url": {"url": image_data_url}}
        ]}],
        temperature=0,
    )
    raw_text = vision_completion.choices[0].message.content.strip()

    # 2. Structured JSON Extraction: Convert raw text to JSON
    json_completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system", 
                "content": (
                    "You are a JSON extractor. Output ONLY raw JSON matching the schema. "
                    "For 'total_amount', provide a numeric value ONLY. Remove currency symbols ($) "
                    "and thousands separators (commas) from the number. No conversational text."
                )
            },
            {"role": "user", "content": f"Extract invoice_number, invoice_date, total_amount, and vendor into JSON from:\n{raw_text}"}
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    
    content = json_completion.choices[0].message.content.strip()

    # --- Error Handling & JSON Repair ---
    if not content:
        raise ValueError("LLM returned an empty response.")

    try:
        structured_data = json.loads(content)
    except json.JSONDecodeError:
        # Attempt to find JSON block if LLM included extra text
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            structured_data = json.loads(match.group())
        else:
            raise ValueError(f"Failed to parse JSON. Content: {content}")

    # --- Data Cleaning (The Float Fix) ---
    raw_amount = structured_data.get("total_amount", 0.0)
    final_amount = 0.0

    if isinstance(raw_amount, str):
        # Remove anything that isn't a digit or a decimal point (e.g., $, commas, letters)
        clean_amount = re.sub(r'[^\d.]', '', raw_amount)
        try:
            # Check if clean_amount is empty after regex (happens if text was provided instead of numbers)
            final_amount = float(clean_amount) if clean_amount else 0.0
        except ValueError:
            final_amount = 0.0
    else:
        # It's already a number
        try:
            final_amount = float(raw_amount)
        except (TypeError, ValueError):
            final_amount = 0.0

    # --- Final Validation & Construction ---
    validated_data = {
        "invoice_number": str(structured_data.get("invoice_number", "N/A")),
        "invoice_date": str(structured_data.get("invoice_date", "N/A")),
        "total_amount": final_amount,
        "vendor": str(structured_data.get("vendor", "Unknown"))
    }
    
    return raw_text, validated_data