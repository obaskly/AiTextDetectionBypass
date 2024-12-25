from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate
from pypdf import PdfReader, PdfWriter
from io import BytesIO
import os 

def get_output_filename(input_path):
    base_dir = os.path.dirname(input_path)
    ext = os.path.splitext(input_path)[1]
    return os.path.join(base_dir, f"paraphrased{ext}")

def save_as_docx(input_path, paraphrased_text):
    try:
        output_path = get_output_filename(input_path)
        
        if os.path.exists(output_path):
            doc = Document(output_path)
        else:
            doc = Document()
        
        doc.add_paragraph(paraphrased_text)
        doc.save(output_path)
        print(f"Successfully saved paraphrased text to {output_path}")
    except Exception as e:
        raise ValueError(f"Error saving docx: {str(e)}")

def save_as_txt(input_path, paraphrased_text):
    try:
        output_path = get_output_filename(input_path)

        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(paraphrased_text + '\n') 
        
        print(f"Successfully saved paraphrased text to {output_path}")
    except Exception as e:
        raise ValueError(f"Error saving txt: {str(e)}")

def save_as_pdf(input_path, paraphrased_text):
    try:
        output_path = get_output_filename(input_path)

        # Create a temporary PDF for the new chunk
        packet = BytesIO()
        
        # Set up the document with margins
        doc = SimpleDocTemplate(
            packet,
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

        # Prepare content with a blank line between chunks
        story = []
        if paraphrased_text.strip():
            story.append(Paragraph(paraphrased_text, style))
            # Add an empty line for spacing
            story.append(Paragraph("", style))

        # Build the temporary PDF
        doc.build(story)

        # Move to the beginning of the buffer
        packet.seek(0)
        new_pdf = PdfReader(packet)

        # If output PDF already exists, append to it
        if os.path.exists(output_path):
            existing_pdf = PdfReader(output_path)
            writer = PdfWriter()
            for page in existing_pdf.pages:
                writer.add_page(page)
            for page in new_pdf.pages:
                writer.add_page(page)
        else:
            # If the file does not exist, only write the new PDF
            writer = PdfWriter()
            for page in new_pdf.pages:
                writer.add_page(page)

        # Save the updated PDF
        with open(output_path, "wb") as output_file:
            writer.write(output_file)

        print(f"Successfully saved paraphrased text to {output_path}")
    except Exception as e:
        raise ValueError(f"Error saving PDF: {str(e)}")
