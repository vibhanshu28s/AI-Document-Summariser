import docx
import os
from google import genai

import os
from dotenv import load_dotenv

load_dotenv()

AI_API = os.getenv("GEMINI_API_KEY")

# 1. Configuration

client = genai.Client(api_key=AI_API)


def extract_text_from_docx(file_path):
    if not os.path.exists(file_path):
        return None
    doc = docx.Document(file_path)
    full_content = [p.text for p in doc.paragraphs if p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            row_data = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_data:
                full_content.append(" | ".join(row_data))
    return "\n".join(full_content)


def generate_summary(text):
    # Note: Ensure gemini-2.0-flash or gemini-1.5-flash is used if 2.5 isn't out yet!
    model_id = "gemini-2.5-flash"

    prompt = f"""
    You are analyzing a document of unknown type.
    Your task is to extract a structured summary that works for legal, technical, financial, operational, insurance, compliance, real-estate, HR, procurement, project, policy, invoice, report, and communication documents.

    Use a professional auditor's tone: objective, structured, concise, and evidence-based.
    Only use information explicitly present in the document.
    Do not invent facts.
    If a section is not available, write "Not stated" or "N/A".

    Extract and summarize the document under the following headings:

    ## 1. DOCUMENT IDENTITY
    - Document Type
    - Title / Reference Number
    - Primary Entities
    - Relevant Dates

    ## 2. EXECUTIVE SUMMARY
    Provide exactly 3 sentences:
    - Sentence 1: What the document is
    - Sentence 2: Its purpose
    - Sentence 3: Its main implication, outcome, or significance

    ## 3. CRITICAL DATA POINTS
    Capture the most important:
    - Numbers, values, measurements, and deadlines
    - IDs, codes, account numbers, site/property references, or policy/contract numbers
    - Addresses, locations, jurisdictions, and facilities
    - Technical, legal, operational, or financial specifics

    ## 4. REQUIREMENTS, ACTIONS & OBLIGATIONS
    Identify:
    - Required actions
    - Responsible party
    - Due dates / timelines
    - Constraints, dependencies, exclusions, or compliance conditions

    ## 5. RISKS, WARNINGS & SPECIAL NOTES
    Highlight:
    - Red flags
    - Warnings
    - Exceptions
    - Penalties
    - Legal or compliance concerns
    - Missing, inconsistent, or ambiguous information
    - Special terms or conditions

    ## 6. FINAL ASSESSMENT
    Provide a brief concluding note on the overall importance or sensitivity of the document.

    Return the answer in clean markdown bullet format.

    DOCUMENT CONTENT:
    {text}
    """


    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"\nFinal Error: {e}"


def save_summary_to_docx(summary_text, output_path):
    """Saves the generated markdown summary into a formatted Word document."""
    doc = docx.Document()
    doc.add_heading('Document Summary', 0)

    # Simple parsing: break text into lines to handle basic formatting
    for line in summary_text.split('\n'):
        line = line.strip()
        if not line:
            continue

        if line.startswith('##'):
            doc.add_heading(line.replace('##', '').strip(), level=1)
        elif line.startswith('-'):
            doc.add_paragraph(line.replace('-', '', 1).strip(), style='List Bullet')
        else:
            doc.add_paragraph(line)

    doc.save(output_path)
    print(f"Summary saved successfully to: {output_path}")


# --- Execution ---
file_name = "summary_output/Summary_output.docx"
output_name = "Summary_output.docx"
content = extract_text_from_docx(file_name)

if content:
    print(f"Summarizing {file_name}...")
    summary = generate_summary(content)

    if "Final Error" not in summary:
        print("Generation complete. Saving to file...")
        save_summary_to_docx(summary, output_name)
        print(summary)
    else:
        print(summary)
else:
    print("File not found.")