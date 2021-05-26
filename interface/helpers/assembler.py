import tempfile
import os
from html.parser import HTMLParser
from markdownify import markdownify


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


def html_to_markdown(html):
    return markdownify(html)


def assemble_content(content, partfiles):
    new_html = replace_cids(content, partfiles)
    # new_markdown = html_to_markdown(new_html)
    return new_html


def cleanup_tempfiles(partfiles):
    for fn in partfiles.values():
        os.remove(fn)
