import os
import sys
from docx import Document
from pypdf import PdfReader, PdfWriter
import pyperclip

def save_as_docx(input_path, paraphrased_text):
    """Save paraphrased text as docx file"""
    try:
        doc = Document()
        doc.add_paragraph(paraphrased_text)
        output_path = get_output_filename(input_path)
        doc.save(output_path)
        print(f"Successfully saved paraphrased text to {output_path}")
    except Exception as e:
        print(f"Error saving docx: {str(e)}")
        sys.exit(1)

def save_as_txt(input_path, paraphrased_text):
    """Save paraphrased text as txt file"""
    try:
        output_path = get_output_filename(input_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(paraphrased_text)
        print(f"Successfully saved paraphrased text to {output_path}")
    except Exception as e:
        print(f"Error saving txt: {str(e)}")
        sys.exit(1)

def save_as_pdf(input_path, paraphrased_text):
    """Save paraphrased text as pdf file with proper formatting"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import Paragraph, SimpleDocTemplate
        from reportlab.lib.units import inch
        
        output_path = get_output_filename(input_path)
        
        # Create document with margins
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Define paragraph style
        style = ParagraphStyle(
            'Normal',
            fontSize=12,
            leading=16,
            spaceBefore=12,
            spaceAfter=12,
            firstLineIndent=24
        )
        
        # Convert text to paragraphs
        story = []
        paragraphs = paraphrased_text.split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), style))
        
        # Build PDF
        doc.build(story)
        print(f"Successfully saved paraphrased text to {output_path}")
        
    except Exception as e:
        print(f"Error saving pdf: {str(e)}")
        sys.exit(1)

def get_output_filename(input_path):
    """Generate output filename by adding '_paraphrased' before extension"""
    base, ext = os.path.splitext(input_path)
    return f"{base}_paraphrased{ext}"

def save_paraphrased_text(input_path):
    """Main function to save paraphrased text in same format as input"""
    # Get paraphrased text from clipboard
    paraphrased_text = pyperclip.paste()
    
    # Get file extension
    _, ext = os.path.splitext(input_path)
    ext = ext.lower()
    
    # Save in appropriate format
    if ext == '.docx':
        save_as_docx(input_path, paraphrased_text)
    elif ext == '.txt':
        save_as_txt(input_path, paraphrased_text)
    elif ext == '.pdf':
        save_as_pdf(input_path, paraphrased_text)
    else:
        print(f"Unsupported file format: {ext}")
        sys.exit(1)