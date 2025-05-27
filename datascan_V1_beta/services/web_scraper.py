import requests
from bs4 import BeautifulSoup

def scrape_website(url, mode='structured'):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if mode == 'structured':
            fields = {}
            # Encontrar campos comuns
            inputs = soup.find_all(['input', 'textarea'])
            for inp in inputs:
                if inp.get('name'):
                    fields[inp['name']] = inp.get('value', '')
            
            # Encontrar textos com padrão label: valor
            texts = []
            for element in soup.find_all(text=True):
                if ':' in element:
                    texts.append(element.split(':')[0] + ': ')
            
            return f"Campos encontrados:\n{fields}\n\nTextos processados:\n{texts}"
        else:
            return soup.get_text(separator='\n', strip=True)
    
    except Exception as e:
        return f"Erro: {str(e)}"