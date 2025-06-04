import google.generativeai as genai
from docx import Document
from fpdf import FPDF
import pandas as pd
import os
from dotenv import load_dotenv
import re

load_dotenv()

class AITerminal:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        self.conversation_state = {
            'awaiting_response': False,
            'document_type': None,
            'fields': [],
            'content': None,
            'formatting': {}
        }
        self.initialize_model()
        
    def initialize_model(self):
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                return True
            except Exception as e:
                print(f"Erro na inicialização: {e}")
                return False
        return False

    def generate_response(self, prompt):
        if not self.model:
            return "Erro: Configure sua API Key primeiro!", None
            
        try:
            if not self.conversation_state['awaiting_response']:
                self._reset_conversation()
                return self._init_document_creation(prompt)
            else:
                return self._handle_document_details(prompt)
                
        except Exception as e:
            return f"Erro na geração: {str(e)}", None

    def _init_document_creation(self, prompt):
        doc_type = self._detect_document_type(prompt)
        if doc_type:
            self.conversation_state.update({
                'awaiting_response': True,
                'document_type': doc_type
            })
            return (
                f"Vou ajudar com o {doc_type.upper()}. Por favor, informe:\n"
                "1. Quais campos devem ser incluídos (separados por vírgula)\n"
                "2. Algum conteúdo base específico?\n"
                "3. Formatação especial (tabelas, cores, etc.)\n"
                "Exemplo: 'Nome, Data, Hora | Texto base: Contrato | Tabela com 3 colunas'",
                None
            )
        else:
            response = self.model.generate_content(prompt)
            return response.text, None

    def _handle_document_details(self, user_input):
        details = [part.strip() for part in user_input.split('|')]
        
        if len(details) > 0:
            self.conversation_state['fields'] = [f.strip() for f in details[0].split(',')]
            
        if len(details) > 1 and ':' in details[1]:
            self.conversation_state['content'] = details[1].split(':')[-1].strip()
            
        if len(details) > 2:
            self._process_formatting(details[2])
            
        file_path = self._create_document()
        self._reset_conversation()
        
        return f"Documento gerado com sucesso!\nLocal: {file_path}", file_path

    def _create_document(self):
        doc_type = self.conversation_state['document_type']
        
        if doc_type == 'docx':
            return self._create_custom_docx()
        elif doc_type == 'pdf':
            return self._create_custom_pdf()
        elif doc_type == 'excel':
            return self._create_custom_excel()
        else:
            return "Tipo de documento não suportado"

    def _create_custom_docx(self):
        doc = Document()
        
        if self.conversation_state['content']:
            doc.add_heading(self.conversation_state['content'], level=0)
            
        for field in self.conversation_state['fields']:
            doc.add_paragraph(f"{field}: ___________________")
            
        if 'table' in self.conversation_state['formatting']:
            cols = self.conversation_state['formatting']['table'].get('columns', 2)
            table = doc.add_table(rows=1, cols=cols)
            
        filename = "documento_personalizado.docx"
        doc.save(filename)
        return os.path.abspath(filename)

    def _create_custom_pdf(self):
        filename = "documento_personalizado.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        if self.conversation_state['content']:
            pdf.cell(200, 10, txt=self.conversation_state['content'], ln=1, align='C')
        
        for field in self.conversation_state['fields']:
            pdf.cell(200, 10, txt=f"{field}: ___________________", ln=1)
        
        pdf.output(filename)
        return os.path.abspath(filename)

    def _create_custom_excel(self):
        filename = "documento_personalizado.xlsx"
        df = pd.DataFrame(columns=self.conversation_state['fields'])
        
        if self.conversation_state['content']:
            df.loc[0] = [self.conversation_state['content']] + [''] * (len(self.conversation_state['fields']) - 1)
        
        df.to_excel(filename, index=False)
        return os.path.abspath(filename)

    def _reset_conversation(self):
        self.conversation_state = {
            'awaiting_response': False,
            'document_type': None,
            'fields': [],
            'content': None,
            'formatting': {}
        }
        
    def _detect_document_type(self, text):
        text = text.lower()
        if 'docx' in text or 'word' in text: return 'docx'
        if 'pdf' in text: return 'pdf'
        if 'excel' in text or 'planilha' in text or 'xlsx' in text: return 'excel'
        return None

    def _process_formatting(self, formatting_text):
        if 'tabela' in formatting_text.lower():
            cols = 2
            if 'colunas' in formatting_text.lower():
                try:
                    cols = int(re.search(r'\d+', formatting_text).group())
                except:
                    pass
            self.conversation_state['formatting']['table'] = {'columns': cols}