import os
from markdown import markdown
from weasyprint import HTML
import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_sketch_files():
    sketch_files = []
    for item in sorted(os.listdir(BASE_DIR)):
        item_path = os.path.join(BASE_DIR, item)
        sketch_path = os.path.join(item_path, 'sketch.md')
        if os.path.isdir(item_path) and os.path.isfile(sketch_path):
            sketch_files.append((item, sketch_path))
    return sketch_files

def build_html(sketch_files, include_toc=True, page_numbers=None):
    """
    Monta o HTML com os conteúdos e o sumário.
    Se page_numbers for dict {app_name: page_num}, inclui os números no sumário.
    """
    body_parts = [
        '<div style="page-break-after: always;">'
        '<h1 style="text-align:center; font-size: 3em; margin-top: 5em;">CRM Partners: Docs</h1>'
        '<p style="text-align:center; font-size: 1.2em; color: #888;">autogenerate documentation</p>'
        '</div>'
    ]

    if include_toc:
        toc_parts = ['<h2>Sumário</h2><ul>']
        for app_name, _ in sketch_files:
            anchor = app_name.replace(' ', '_').lower()
            page_num_display = ''
            if page_numbers and app_name in page_numbers:
                page_num_display = f'<span style="float:right;">{page_numbers[app_name]}</span>'
            toc_parts.append(
                f'<li style="position: relative; padding-right: 30px;">'
                f'📄 <a href="#{anchor}">{app_name}</a>{page_num_display}'
                '</li>'
            )
        toc_parts.append('</ul><hr>')
        body_parts.extend(toc_parts)

    for app_name, file_path in sketch_files:
        anchor = app_name.replace(' ', '_').lower()
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            html = markdown(content, extensions=["tables", "fenced_code"])
            # Marca o título com id para o link
            body_parts.append(f'<h2 id="{anchor}">{app_name}</h2>{html}<hr>')

    full_html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4;
                margin: 2cm;
                @bottom-center {{
                    content: "Página " counter(page) " de " counter(pages);
                    font-size: 0.8em;
                    color: #555;
                }}
            }}
            body {{
                font-family: Arial, sans-serif;
                margin: 2em;
            }}
            h1, h2 {{
                color: #2c3e50;
            }}
            ul {{
                list-style-type: none;
                padding-left: 0;
            }}
            ul li {{
                margin-bottom: 0.5em;
                font-size: 1.1em;
                position: relative;
            }}
            ul li a {{
                text-decoration: none;
                color: #2980b9;
            }}
            ul li a:hover {{
                text-decoration: underline;
            }}
            ul li span {{
                position: absolute;
                right: 0;
                top: 0;
                font-weight: bold;
                color: #555;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 1.5em;
            }}
            table, th, td {{
                border: 1px solid #ddd;
            }}
            th, td {{
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            code {{
                background-color: #eee;
                padding: 2px 4px;
                font-family: monospace;
            }}
            pre {{
                background-color: #f5f5f5;
                padding: 1em;
                overflow: auto;
            }}
        </style>
    </head>
    <body>
        {''.join(body_parts)}
    </body>
    </html>
    """
    return full_html

def generate_pdf(html_content, output_file):
    HTML(string=html_content).write_pdf(output_file)

def extract_page_numbers(pdf_file, sketch_files):
    """
    Usa PyMuPDF para abrir o PDF e buscar a página de cada app_name.
    Assumimos que o título aparece como "AppName" (h2) no texto.
    Retorna dict {app_name: page_num}.
    """
    doc = fitz.open(pdf_file)
    page_numbers = {}
    for page_index in range(len(doc)):
        page = doc[page_index]
        text = page.get_text()
        for app_name, _ in sketch_files:
            if app_name in text and app_name not in page_numbers:
                # Contagem de página começa em 1 no PDF
                page_numbers[app_name] = page_index + 1
    doc.close()
    return page_numbers

if __name__ == "__main__":
    sketch_files = get_sketch_files()

    # 1º passo: gerar PDF temporário sem sumário para detectar as páginas corretas
    html_initial = build_html(sketch_files, include_toc=False, page_numbers=None)
    temp_pdf = "temp_manual.pdf"
    generate_pdf(html_initial, temp_pdf)

    # 2º passo: extrair números das páginas de cada app_name
    pages = extract_page_numbers(temp_pdf, sketch_files)
    print("Páginas detectadas:", pages)

    # 3º passo: gerar PDF final com sumário e números no sumário
    html_final = build_html(sketch_files, include_toc=True, page_numbers=pages)
    final_pdf = "project_documentation.pdf"
    generate_pdf(html_final, final_pdf)

    # Apaga o PDF temporário
    os.remove(temp_pdf)

    print(f"final pdf ready: {final_pdf}")

