from docx import Document
import pandas as pd
import PyPDF2
import io

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
    new_path = f"processed_{path.split('/')[-1]}"
    doc.save(new_path)
    return f"DOCX processado: {new_path}"

def process_pdf(path):
    with open(path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()
        
        for page in reader.pages:
            text = page.extract_text()
            lines = [line.split(':')[0] + ': ' for line in text.split('\n') if ':' in line]
            new_text = '\n'.join(lines)
            
            # Criar nova página
            new_page = PyPDF2.PageObject.create_blank_page(
                width=page.mediabox.width,
                height=page.mediabox.height
            )
            new_page.merge_page(page)
            new_page.add_text(new_text)
            
            writer.add_page(new_page)
        
        new_path = f"processed_{path.split('/')[-1]}"
        with open(new_path, 'wb') as output_file:
            writer.write(output_file)
        return f"PDF processado: {new_path}"

def process_excel(path):
    df = pd.read_excel(path) if path.endswith(('.xlsx', '.xls')) else pd.read_csv(path)
    
    # Limpar células que seguem padrão "Label: Valor"
    for col in df.columns:
        df[col] = df[col].apply(lambda x: x.split(':')[0] + ': ' if isinstance(x, str) and ':' in x else x)
    
    new_path = f"processed_{path.split('/')[-1]}"
    df.to_excel(new_path, index=False) if path.endswith(('.xlsx', '.xls')) else df.to_csv(new_path, index=False)
    return f"Excel processado: {new_path}"