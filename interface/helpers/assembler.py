import tempfile
import os
from html.parser import HTMLParser


def replace_cids(content, partfiles):

    class Parser(HTMLParser):

        new_html = ''

        def handle_starttag(self, tag, attrs):
            new_attrs = ''
            for attr, value in attrs:
                if attr == 'width' or attr == 'height':
                    continue
                elif attr == 'src' and tag == 'img':
                    cid = value.split("cid:")[1]
                    if cid in partfiles:
                        value = partfiles[cid]

                new_attrs += "{}=\"{}\" ".format(attr, value)
            self.new_html += "<{} {}>".format(tag, new_attrs)

        def handle_endtag(self, tag):
            self.new_html += "</{}>".format(tag)

        def handle_data(self, data):
            self.new_html += data

    parser = Parser()
    parser.feed(content)
    return parser.new_html


def assemble_file(content, partfiles):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(replace_cids(content, partfiles))

    return f.name


def create_new_filename():
    return ''


def cleanup_temp_files(temp_html, partfiles):
    os.remove(temp_html)
    for fn in partfiles.values():
        os.remove(fn)
