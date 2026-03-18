import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Document Summariser", page_icon="📄")

st.title("📄 Document Summariser")
st.write("Upload a PDF to Generate Summarized Report.")

# File Uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Define the save folder and path
    save_folder = 'uploaded_files_dir'
    # Create the directory if it doesn't exist
    Path(save_folder).mkdir(parents=True, exist_ok=True)
    save_path = Path(save_folder, uploaded_file.name)

    # Write the file to disk in binary mode
    with open(save_path, mode='wb') as w:
        w.write(uploaded_file.getvalue())


    if st.button("Process & Summarize"):
        with st.spinner("Processing document... this may take a moment."):
            try:
                import os
                import fitz  # PyMuPDF
                import pdfplumber
                from docx import Document
                from docx.shared import Inches
                import logging

                # Setup basic logging
                logging.basicConfig(level=logging.INFO)


                class EngineeringToDoc:
                    def __init__(self, pdf_path):
                        self.pdf_path = pdf_path
                        self.doc = Document()

                    def convert(self, output_path):
                        # We use fitz (PyMuPDF) to handle the drawing/image snapshots
                        pdf_images = fitz.open(self.pdf_path)

                        # We use pdfplumber to handle the text and table logic
                        with pdfplumber.open(self.pdf_path) as pdf:
                            for i, page in enumerate(pdf.pages):
                                logging.info(f"Processing Page {i + 1}...")

                                # 1. ADD TEXT 'AS IS'
                                text = page.extract_text()
                                if text:
                                    self.doc.add_paragraph(text)

                                # 2. ADD TABLES 'AS IS'
                                tables = page.extract_tables()
                                for table in tables:
                                    if not table: continue
                                    docx_table = self.doc.add_table(rows=len(table), cols=len(table[0]))
                                    docx_table.style = 'Table Grid'
                                    for r_idx, row in enumerate(table):
                                        for c_idx, cell in enumerate(row):
                                            docx_table.cell(r_idx, c_idx).text = str(cell) if cell else ""

                                # 3. ADD ENGINEERING DRAWING AS IMAGE
                                # This captures the visual layout (drawings, logos, stamps)
                                pix = pdf_images[i].get_pixmap(matrix=fitz.Matrix(2, 2))  # High res
                                img_path = f"temp_page_{i}.png"
                                pix.save(img_path)

                                self.doc.add_heading(f'Drawing/Layout Snapshot - Page {i + 1}', level=2)
                                self.doc.add_picture(img_path, width=Inches(6.0))

                                # Cleanup temp image
                                os.remove(img_path)
                                self.doc.add_page_break()

                        self.doc.save(output_path)
                        pdf_images.close()
                        logging.info(f"Success! Saved to {output_path}")


                # --- EXECUTION ---
                if __name__ == "__main__":
                    # 1. Update these paths
                    INPUT_PDF = f"uploaded_files_dir/{uploaded_file.name}"
                    OUTPUT_DOCX = f"parser_file_output/{uploaded_file.name}_parsed.docx"

                    # 2. Run the tool
                    converter = EngineeringToDoc(INPUT_PDF)
                    converter.convert(OUTPUT_DOCX)

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
                file_name = f"parser_file_output/{uploaded_file.name}_parsed.docx"
                output_name = "summary_output/Summary_output.docx"
                content = extract_text_from_docx(file_name)

                if content:
                    print(f"Summarizing {file_name}...")
                    summary = generate_summary(content)

                    if "Final Error" not in summary:
                        print("Generation complete. Saving to file...")
                        save_summary_to_docx(summary, output_name)
                        print(summary)
                        st.text(summary)
                    else:
                        print(summary)
                else:
                    print("File not found.")


            except Exception as e:
                st.error(f"An error occurred: {e}")