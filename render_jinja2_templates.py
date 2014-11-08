import codecs
import glob
import os
import re
import subprocess
import tempfile

from jinja2 import Environment, PackageLoader


ENV = Environment(loader=PackageLoader(__name__, 'content'))
NODE_SCRIPT_TEMPLATE = u"""\
katex = require('katex');
value = katex.renderToString("%s");
console.log(value);
"""


def escape_string(latex_str):
    return latex_str.replace('\\', r'\\')


def get_katex(latex_str):
    escaped = escape_string(latex_str)
    script_content = NODE_SCRIPT_TEMPLATE % (escaped,)

    temp_script = tempfile.mktemp()
    with open(temp_script, 'w') as fh:
        fh.write(script_content)

    result = subprocess.check_output(['node', temp_script])
    return result.strip().decode('utf8')


def get_templates():
    result = []
    for match in glob.glob('content/*.template'):
        directory, template_name = os.path.split(match)
        if directory != 'content':
            raise ValueError(match)

        template = ENV.get_template(template_name)
        result.append(template)

    return result


def write_template(template):
    name, ext = os.path.splitext(template.name)
    if ext != '.template':
        raise ValueError(template.name)

    # This assumes we are running in the root of the repository.
    new_filename = 'content/%s.md' % (name,)
    print 'Writing', new_filename
    with codecs.open(new_filename, 'wb', 'utf-8') as fh:
        rendered_file = template.render(get_katex=get_katex)
        fh.write(rendered_file)
        # Make sure the file has a trailing newline.
        if rendered_file[-1] != '\n':
            fh.write('\n')


if __name__ == '__main__':
    for template in get_templates():
        write_template(template)
