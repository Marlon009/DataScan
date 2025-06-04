from docx import Document
import pandas as pd
import PyPDF2
import os
from fpdf import FPDF

def process_file(file_path):
    try:
        if file_path.endswith('.docx'):
            return process_docx(file_path)
        elif file_path.endswith('.pdf'):
            return process_pdf(file_path)
        elif file_path.endswith(('.xlsx', '.xls', '.csv')):
            return process_excel(file_path)
        else:
            return "Formato não suportado"
    except Exception as e:
        return f"Erro: {str(e)}"

def process_docx(path):
    doc = Document(path)
    for para in doc.paragraphs:
        if ':' in para.text:
            para.text = para.text.split(':')[0] + ': '
    new_path = f"processed_{os.path.basename(path)}"
    doc.save(new_path)
    return f"DOCX processado: {new_path}"

def process_pdf(path):
    with open(path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    
    processed_text = "\n".join([line.split(':')[0] + ': ' 
                              for line in text.split('\n') if ':' in line])
    
    new_path = f"processed_{os.path.basename(path)}"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, processed_text)
    pdf.output(new_path)
    
    return f"PDF processado: {new_path}"

def process_excel(path):
    df = pd.read_excel(path) if path.endswith(('.xlsx', '.xls')) else pd.read_csv(path)
    
    for col in df.columns:
        df[col] = df[col].apply(lambda x: x.split(':')[0] + ': ' if isinstance(x, str) and ':' in x else x)
    
    new_path = f"processed_{os.path.basename(path)}"
    if path.endswith(('.xlsx', '.xls')):
        df.to_excel(new_path, index=False)
    else:
        df.to_csv(new_path, index=False)
    return f"Excel processado: {new_path}"