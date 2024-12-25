import docx
from pypdf import PdfReader
import nltk
import re

try:
    nltk.download('punkt')
except:
    nltk.download('punkt')

def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        raw_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        return format_text(raw_text)
    except Exception as e:
        return f"Error reading DOCX file: {e}"

def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        raw_text = '\n'.join([page.extract_text() for page in reader.pages])
        return format_text(raw_text)
    except Exception as e:
        raise ValueError(f"Error reading PDF file: {e}")

def format_text(text):
    text = remove_unnecessary_line_breaks(text)
    sentences = nltk.sent_tokenize(text)
    formatted_text = ' '.join(sentences)
    return formatted_text

def remove_unnecessary_line_breaks(text):
    # Replace line breaks followed by non-uppercase letters with a space
    cleaned_text = re.sub(r'\n(?![A-Z])', ' ', text)
    # Replace multiple spaces with a single space
    cleaned_text = re.sub(r' +', ' ', cleaned_text)
    return cleaned_text.strip()
