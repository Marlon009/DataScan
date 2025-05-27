from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLineEdit, QPushButton, QTextEdit,
    QComboBox, QLabel, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QEvent
from services.file_processor import process_file
from services.web_scraper import scrape_website
from services.ai_terminal import AITerminal
import os

class DataScan(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataScan Pro")
        self.setGeometry(100, 100, 1200, 800)
        self.ai = AITerminal()
        self.init_ui()
        self.apply_styles()
        self.ai_input.installEventFilter(self)
        self.current_file_path = None
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return and not event.modifiers():
            if self.ai_input.hasFocus():
                self.handle_ai_input()
        else:
            super().keyPressEvent(event)
            
        
    def eventFilter(self, source, event):
        if (event.type() == QEvent.Type.KeyPress and
            source is self.ai_input and
            event.key() == Qt.Key.Key_Return and
            not event.modifiers()):
            
            self.handle_ai_input()
            return True
        return super().eventFilter(source, event)

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        # File Processing Tab
        file_tab = QWidget()
        self.init_file_tab(file_tab)
        tabs.addTab(file_tab, "📁 Arquivos")

        # Web Scraping Tab
        web_tab = QWidget()
        self.init_web_tab(web_tab)
        tabs.addTab(web_tab, "🌐 Web")

        # AI Terminal Tab
        ai_tab = QWidget()
        self.init_ai_tab(ai_tab)
        tabs.addTab(ai_tab, "🤖 IA")

    def init_file_tab(self, tab):
        layout = QVBoxLayout(tab)
        self.ai_input = QLineEdit()
        self.ai_input.setPlaceholderText("Digite e pressione Enter para enviar (Shift+Enter para nova linha)")
        
        # File Selection
        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        btn_browse = QPushButton("Selecionar Arquivo")
        btn_browse.clicked.connect(self.browse_file)
        
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(btn_browse)
        
        # Preview
        self.preview = QTextEdit()
        
        # Processing
        btn_process = QPushButton("Processar")
        btn_process.clicked.connect(self.process_file)
        
        layout.addLayout(file_layout)
        layout.addWidget(self.preview)
        layout.addWidget(btn_process)

    def init_web_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # URL Input
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        btn_scrape = QPushButton("Escanear")
        btn_scrape.clicked.connect(self.scrape_web)
        
        url_layout.addWidget(QLabel("URL:"))
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(btn_scrape)
        
        # Results
        self.web_results = QTextEdit()
        
        layout.addLayout(url_layout)
        layout.addWidget(self.web_results)

    def init_ai_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # Seção de API Key
        key_layout = QHBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Cole sua API Key do Gemini aqui...")
        btn_save_key = QPushButton("🔑 Salvar")
        btn_save_key.clicked.connect(self.save_api_key)
        
        key_layout.addWidget(self.api_key_input)
        key_layout.addWidget(btn_save_key)
        
        # Histórico do chat
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        
        # Entrada do usuário
        input_layout = QHBoxLayout()
        self.ai_input = QLineEdit()
        self.ai_input.setPlaceholderText("Digite sua solicitação...")
        btn_send = QPushButton("🚀 Enviar")
        btn_send.clicked.connect(self.handle_ai_input)
        
        input_layout.addWidget(self.ai_input)
        input_layout.addWidget(btn_send)
        
        layout.addLayout(key_layout)
        layout.addWidget(self.chat_history)
        layout.addLayout(input_layout)
        
    def create_interactive_buttons(self):
        # Adicione isso no final do init_ai_tab
        btn_open = QPushButton("Abrir Documento")
        btn_open.clicked.connect(self.open_document)
        self.chat_history.addWidget(btn_open)

    def open_document(self):
        if self.current_file_path:
            os.startfile(self.current_file_path)
        
    def save_api_key(self):
        key = self.api_key_input.text().strip()
        if key:
            self.ai = AITerminal(api_key=key)
            QMessageBox.information(self, "Sucesso", "Chave configurada com sucesso!")
        else:
            QMessageBox.warning(self, "Aviso", "Insira uma API Key válida!")

    def apply_styles(self):
        self.setStyleSheet("""
            QTextEdit, QLineEdit {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #0078d4;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #006cbd;
            }
            QMainWindow {
                background-color: #f0f0f0;
            }
        """)

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo", "", 
            "Documentos (*.docx *.pdf *.xlsx *.xls *.csv)"
        )
        if path:
            self.file_path.setText(path)
            self.preview.setText(f"Arquivo selecionado: {path}")

    def process_file(self):
        path = self.file_path.text()
        if path:
            result = process_file(path)
            self.preview.setText(result)
            QMessageBox.information(self, "Sucesso", "Arquivo processado!")

    def scrape_web(self):
        url = self.url_input.text()
        if url:
            result = scrape_website(url)
            self.web_results.setText(result)

    def handle_ai_input(self):
        user_text = self.ai_input.text()
        if not user_text:
            return
            
        self.chat_history.append(f"Você: {user_text}")
        self.ai_input.clear()
        
        response, file_path = self.ai.generate_response(user_text)
        
        if file_path:
            self.current_file_path = file_path
            self.chat_history.append(f"IA: {response}\n[Abrir Documento]({file_path})")
        else:
            self.chat_history.append(f"IA: {response}")
        
        # Rolagem automática para a última mensagem
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum()
        )

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication([])
    window = DataScan()
    window.show()
    app.exec()