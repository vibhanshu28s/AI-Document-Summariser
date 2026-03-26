import json
from google import genai
from google.genai import types
from docx import Document
import os
from dotenv import load_dotenv
from scipy.constants import precision

load_dotenv()

AI_API = os.getenv("GEMINI_API_KEY")
# Initialize Client
client = genai.Client(api_key=AI_API)

# 1. Load the PDF
pdf_path = "input.pdf"
with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

# 2. Generate Content
# Prompting for Markdown helps maintain structure for the Word doc conversion
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        """Perform a high-fidelity OCR and layout extraction on this PDF. 

        STRICT REQUIREMENTS:
        1. STRUCTURE: Maintain the exact logical flow and hierarchy of the document.
        2. TABLES: Convert every table into a valid Markdown table format.
        3. NO CHATTER: Do not provide any intro, outro, or status updates. Output ONLY the document content.
        4. NO SKIPPING: If a word is blurred, smudged, or partially obscured, do not skip it. Provide the most likely transcription based on surrounding context. If truly illegible, use [? - best guess].
        5. PRECISION: Maintain original capitalization, punctuation, and numerical data exactly as shown.
        6. NO REPETITION: Do not duplicate lines or sections.""",
        types.Part.from_bytes(
            data=pdf_bytes,
            mime_type="application/pdf"
        )
    ]
)

extracted_text = response.text

# ---

### 3. Save as JSON
# We wrap the text in a dictionary to make it a valid JSON file
data_to_save = {
    "source_file": pdf_path,
    "extraction_method": "gemini-2.5-flash",
    "content": extracted_text
}

with open("output.json", "w", encoding="utf-8") as jf:
    json.dump(data_to_save, jf, indent=4, ensure_ascii=False)

print("✅ Saved to output.json")

# ---

### 4. Save as Word (.docx)
doc = Document()
doc.add_heading('Extracted Document Content', 0)

# We split the text by newlines to create proper paragraphs in Word
paragraphs = extracted_text.split('\n')
for p in paragraphs:
    if p.strip():  # Only add non-empty lines
        doc.add_paragraph(p)

doc.save("output.docx")

print("✅ Saved to output.docx")