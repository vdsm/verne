from jinja2 import nodes
from jinja2.ext import Extension


class JinjaComments(Extension):
    tags = {'comments'}

    def __init__(self, environment):
        super(JinjaComments, self).__init__(environment)

