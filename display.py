import docx
from dotenv import load_dotenv
import os
import google.genai as genai


load_dotenv()

AI_API = os.getenv("DISPLAY")

doc = docx.Document("output.docx")


full_text = []
for para in doc.paragraphs:
    full_text.append(para.text)

store='\n'.join(full_text)

client = genai.Client(api_key=AI_API)


try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=store,
        config={
            "system_instruction": "Document Processing Agent, Extract All The Tables present in the Document.",
            "temperature": 0.1
        }
    )

    print(response.text)

except Exception as e:
    print(f"An error occurred: {e}")

