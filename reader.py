import docx
from pypdf import PdfReader

def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        return f"Error reading DOCX file: {e}"

def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        return '\n'.join([page.extract_text() for page in reader.pages])
    except Exception as e:
        raise ValueError(f"Error reading PDF file: {e}")
