from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
from http.server import BaseHTTPRequestHandler


def support_for_mod_operator(myself, dict):
    myself.setData(dict)
    return myself.render(myself.dict)


def support_for_context_variable(myself, dict):
    if not hasattr(myself, "dict"):
        myself.dict = {}
    myself.dict.update(dict)
    return myself


Template.__mod__ = support_for_mod_operator
Template.setData = support_for_context_variable


class JinjaHandler(BaseHTTPRequestHandler):

    env = Environment(
        loader=FileSystemLoader('/app/template'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    error_message_format = env.get_template('error.html')
    error_message_format.setData({'title':"Error response"})
