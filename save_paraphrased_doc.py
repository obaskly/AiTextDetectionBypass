from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate
import os 

def get_output_filename(input_path):
    base_dir = os.path.dirname(input_path)
    ext = os.path.splitext(input_path)[1]
    return os.path.join(base_dir, f"paraphrased{ext}")

def save_as_docx(input_path, paraphrased_text):
    try:
        doc = Document()
        doc.add_paragraph(paraphrased_text)
        output_path = get_output_filename(input_path)
        doc.save(output_path)
        print(f"Successfully saved paraphrased text to {output_path}")
    except Exception as e:
        raise ValueError(f"Error saving docx: {str(e)}")

def save_as_txt(input_path, paraphrased_text):
    try:
        output_path = get_output_filename(input_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(paraphrased_text)
        print(f"Successfully saved paraphrased text to {output_path}")
    except Exception as e:
        raise ValueError(f"Error saving txt: {str(e)}")

def save_as_pdf(input_path, paraphrased_text):
    try:
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
        raise ValueError(f"Error saving pdf: {str(e)}")
