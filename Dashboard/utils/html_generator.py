from jinja2 import Environment, FileSystemLoader
import os

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '../templates')
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def generate_html(context):
    template = env.get_template("dashboard.html")
    return template.render(**context)

def render_project_section(context):
    template = env.get_template("project_dashboard.html")
    return template.render(**context)
