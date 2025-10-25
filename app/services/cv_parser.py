import io
import fitz  # PyMuPDF
from docx import Document


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    pdf_document = fitz.open(stream=file_content, filetype="pdf")
    text = ""

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        text += page.get_text()

    pdf_document.close()
    return text


def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    doc = Document(io.BytesIO(file_content))
    text = []

    for paragraph in doc.paragraphs:
        text.append(paragraph.text)

    return "\n".join(text)


def extract_text_from_text(file_content: bytes) -> str:
    """Extract text from plain text file"""
    return file_content.decode('utf-8')


def parse_file(file_content: bytes, file_type: str) -> str:
    """Parse file and extract text content"""
    file_type_lower = file_type.lower()

    if file_type_lower == 'application/pdf' or file_type.endswith('.pdf'):
        return extract_text_from_pdf(file_content)
    elif file_type_lower in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'] or file_type.endswith(('.docx', '.doc')):
        return extract_text_from_docx(file_content)
    elif file_type_lower in ['text/plain', 'text/markdown'] or file_type.endswith(('.txt', '.md')):
        return extract_text_from_text(file_content)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
