# 📄 Universal Document Summarizer (Gemini AI)

An intelligent Python-based tool that extracts text from various document formats and uses Google's Gemini 1.5 Flash model to generate structured, industry-aware summaries. Whether it's an insurance policy, a property deed, or a technical RFDS (Radio Frequency Design Sheet), this tool identifies the core entities, obligations, and risks.

## ✨ Features
* **Multi-Format Support**: Handles both `.pdf` and `.docx` files.
* **Intelligent Extraction**: Uses `python-docx` for Word tables/text and `pypdf` for PDF data.
* **Universal Prompting**: A carefully engineered prompt that identifies:
    * **Document Identity** (Type, Entities, Dates)
    * **Executive Summary** (High-level goals)
    * **Critical Data Points** (Prices, specs, or measurements)
    * **Obligations** (What needs to be done?)
    * **Risk Assessment** (Red flags or special conditions)
* **Modern SDK**: Built using the latest `google-genai` library.

## 🚀 Quick Start

### 1. Prerequisites
* Python 3.9+
* A Google AI Studio API Key ([Get one here](https://aistudio.google.com/))

### 2. Installation
Clone the repository and install the required dependencies:
```bash
git clone https://github.com/yourusername/universal-summarizer.git
cd universal-summarizer
pip install google-genai python-docx pypdf
```

### 3. Usage
1.  Open the script and replace `YOUR_API_KEY` with your actual Gemini API key.
2.  Place your document (e.g., `policy.pdf` or `site_report.docx`) in the project folder.
3.  Update the `target_file` variable in the script.
4.  Run the application:
```bash
python summarizer.py
```

## 🛠️ How it Works
The script utilizes a **Context-Agnostic Prompt**. Instead of looking for industry-specific keywords, it asks the AI to find "Entities" and "Requirements."

* **Use Python 3.10**