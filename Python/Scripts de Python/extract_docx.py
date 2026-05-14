import zipfile
import xml.etree.ElementTree as ET
import sys

docx_path = "/home/jpmr/Desktop/json to csv planify/Preparação para Prova de Admissão 3º Ano.docx"

try:
    with zipfile.ZipFile(docx_path) as z:
        xml_content = z.read('word/document.xml')
        root = ET.fromstring(xml_content)
        
        # XML namespaces
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        text_content = []
        for p in root.findall('.//w:p', ns):
            para_text = ""
            for t in p.findall('.//w:t', ns):
                if t.text:
                    para_text += t.text
            if para_text:
                text_content.append(para_text)
                
        print("\n".join(text_content))

except Exception as e:
    print(f"Error: {e}")
