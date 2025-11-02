from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import os

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
env = Environment(loader=FileSystemLoader(template_dir))

def create_profile_pdf(profile_data: str) -> bytes:
    template = env.get_template("pdf_template.html")
    html_out = template.render(data=profile_data)
    return HTML(string=html_out).write_pdf()
