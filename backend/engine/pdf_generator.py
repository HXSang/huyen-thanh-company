import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import datetime

def generate_pdf(data_json, nhan_vien, template_name="template.html"): 
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(BASE_DIR, "templates")
    STATIC_DIR = os.path.join(BASE_DIR, "static")

    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template(template_name)

    now = datetime.now()
    
    html_content = template.render(
        khach_hang=data_json.get('khach_hang', {}),
        items=data_json.get('items', []),
        nhan_vien=nhan_vien,
        ngay=f"{now.day:02d}",    
        thang=f"{now.month:02d}",     
        nam=now.year         
    )

    pdf_bytes = HTML(string=html_content, base_url=STATIC_DIR).write_pdf()  
    
    return pdf_bytes