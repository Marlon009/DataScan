import requests
from bs4 import BeautifulSoup
from collections import defaultdict

def scrape_website(url, mode='structured'):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if mode == 'structured':
            # 1. Extrair campos de formulário
            form_fields = {}
            for inp in soup.find_all(['input', 'textarea', 'select']):
                if inp.get('name'):
                    form_fields[inp['name']] = inp.get('value', '')
            
            # 2. Detectar e extrair dados estruturados de forma genérica
            structured_data = []
            
            # Estratégia 1: Encontrar padrões de lista de itens
            list_containers = soup.find_all(['ul', 'ol', 'div', 'section'], class_=True)
            for container in list_containers:
                items = container.find_all(['li', 'div', 'article', 'tr'], recursive=False)
                if len(items) > 3:  # Considerar apenas contêineres com vários itens
                    container_data = extract_container_data(container)
                    if container_data:
                        structured_data.append(container_data)
            
            # Estratégia 2: Encontrar tabelas
            tables = soup.find_all('table')
            for table in tables:
                table_data = extract_table_data(table)
                if table_data:
                    structured_data.append(table_data)
            
            # Estratégia 3: Encontrar pares chave-valor
            key_value_pairs = extract_key_value_pairs(soup)
            
            # Formatando resultado para GUI
            result_str = "=== Campos de Formulário ===\n"
            for name, value in form_fields.items():
                result_str += f"{name}: {value}\n"
            
            result_str += "\n=== Dados Estruturados ===\n"
            for data in structured_data:
                # Dados de contêiner
                if 'items' in data:
                    result_str += f"\n{data['type']}:\n"
                    for item in data['items']:
                        for key, value in item.items():
                            result_str += f"  {key}: {value}\n"
                        result_str += "─" * 40 + "\n"
                # Dados de tabela
                elif 'rows' in data:
                    result_str += f"\nTabela ({data['type']}):\n"
                    result_str += " | ".join(data['headers']) + "\n"
                    for row in data['rows']:
                        result_str += " | ".join(row.values()) + "\n"
            
            result_str += "\n=== Pares Chave-Valor ===\n"
            for key, value in key_value_pairs.items():
                result_str += f"{key}: {value}\n"
            
            return result_str
        
        else:
            return soup.get_text(separator='\n', strip=True)
    
    except Exception as e:
        return f"Erro: {str(e)}"

def extract_container_data(container):
    """Extrai dados de contêineres como listas ou grids"""
    items = container.find_all(['li', 'div', 'article', 'tr'], recursive=False)
    if not items:
        return None
        
    # Tentar identificar o tipo de dado pelo título ou contexto
    container_type = container.get('class', ['Dados'])[0].capitalize()
    
    container_data = {
        'type': container_type,
        'items': []
    }
    
    for item in items:
        item_data = {}
        # Extrair título
        title = item.find(['h2', 'h3', 'h4', 'h5', 'h6', 'strong'])
        if title:
            item_data['title'] = title.get_text(strip=True)
        
        # Extrair pares chave-valor
        key_values = extract_key_value_pairs(item)
        item_data.update(key_values)
        
        # Extrair texto completo se não encontrou pares
        if not key_values:
            item_data['content'] = item.get_text(strip=True, separator='\n')
        
        container_data['items'].append(item_data)
    
    return container_data

def extract_table_data(table):
    """Extrai dados de tabelas"""
    rows = table.find_all('tr')
    if not rows:
        return None
        
    headers = []
    header_row = rows[0].find_all(['th', 'td'])
    for cell in header_row:
        headers.append(cell.get_text(strip=True) or f"Coluna {len(headers)+1}")
    
    table_data = {
        'type': 'Tabela',
        'headers': headers,
        'rows': []
    }
    
    for row in rows[1:]:
        row_data = {}
        cells = row.find_all('td')
        for i, cell in enumerate(cells):
            if i < len(headers):
                header = headers[i]
                row_data[header] = cell.get_text(strip=True)
        if row_data:  # Só adicionar se tiver dados
            table_data['rows'].append(row_data)
    
    return table_data

def extract_key_value_pairs(element):
    """Extrai pares chave-valor de qualquer elemento"""
    key_value_pairs = {}
    
    # Estratégia 1: Elementos com estrutura direta
    for elem in element.find_all(['dt', 'div', 'p', 'span']):
        text = elem.get_text(strip=True)
        if ':' in text:
            parts = text.split(':', 1)
            key = parts[0].strip()
            value = parts[1].strip()
            if key and value:
                key_value_pairs[key] = value
    
    # Estratégia 2: Agrupamentos com rótulos
    for group in element.find_all(['dl', 'div']):
        terms = group.find_all(['dt', 'strong', 'b'])
        for term in terms:
            key = term.get_text(strip=True).rstrip(':')
            next_sib = term.find_next_sibling()
            if next_sib and next_sib.name in ['dd', 'span', 'div']:
                value = next_sib.get_text(strip=True)
                if key and value:
                    key_value_pairs[key] = value
    
    return key_value_pairs