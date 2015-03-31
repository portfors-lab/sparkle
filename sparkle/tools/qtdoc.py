"""Integration of Online Qt classes documentation with Sphinx"""

import re

from docutils import nodes, utils
from docutils.parsers.rst.roles import set_classes


def qtdoc_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """Links to a Qt class's doc

    Returns 2 part tuple containing list of nodes to insert into the
    document and a list of system messages.  Both are allowed to be
    empty.

    :param name: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.
    """
    base = 'http://qt-project.org/doc/qt-4.8/'

    match = re.search('([^<]+)(<[^<>]+>)?', text)
    if match is None:
        raise ValueError

    label = match.group(1)
    if match.lastindex == 2:
        # remove the carots from second group
        clsmeth = match.group(2)[1:-1]
        # assumes single . separating a class and a method or property name
        cls, meth = clsmeth.split('.')
        ref = base + cls + '.html#' + meth
    else:
        ref = base + label.lower() + '.html'

    node = nodes.reference(rawtext, label, refuri=ref, **options)
    return [node], []

def setup(app):
    """Installs the plugin.
    
    :param app: Sphinx application context.
    """
    app.info("Adding Qt doc role")
    app.add_role('qtdoc', qtdoc_role)
