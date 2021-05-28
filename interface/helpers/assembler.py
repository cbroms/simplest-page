import tempfile
import os
import constants
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html.parser import HTMLParser
from markdownify import markdownify
from pybars import Compiler

compiler = Compiler()


def replace_cids(content, partfiles):

    class Parser(HTMLParser):
        new_html = ''
        description = ''
        image = ''

        def handle_starttag(self, tag, attrs):

            new_attrs = ''
            for attr, value in attrs:
                if attr == 'width' or attr == 'height':
                    continue
                elif attr == 'src' and tag == 'img':
                    cid = value.split("cid:")[1]
                    if cid in partfiles:
                        value = partfiles[cid]

                    if self.image == '':
                        self.image = value

                new_attrs += "{}=\"{}\" ".format(attr, value)
            self.new_html += "<{} {}>".format(tag, new_attrs)

        def handle_endtag(self, tag):
            self.new_html += "</{}>".format(tag)

        def handle_data(self, data):
            self.new_html += data
            if len(self.description) < 240:
                self.description += data + ' '

    parser = Parser()
    parser.feed(content)
    return (parser.new_html, parser.image, parser.description)


def html_to_markdown(html):
    return markdownify(html)


def assemble_content(author, title, date, content, partfiles):
    (new_html, image, description) = replace_cids(content, partfiles)
    with open('templates/template.html', 'r') as file:
        source = file.read()
        template = compiler.compile(source)

        output = template({
            'body': new_html,
            'image': image,
            'description': description,
            'author': author,
            'title': title,
            'date': date,
        })

    # new_markdown = html_to_markdown(new_html)
    return output


def assemble_email(old_message, new_message, args=None):
    if args != None:
        template = compiler.compile(new_message)
        new_message = template(args)

    msg = MIMEMultipart('mixed')
    body = MIMEMultipart('alternative')

    msg["Subject"] = "Re: " + old_message.get("Subject")
    msg['In-Reply-To'] = old_message.get("Message-ID")
    msg['References'] = old_message.get("Message-ID")
    msg['Thread-Topic'] = old_message.get("Thread-Topic")
    msg['Thread-Index'] = old_message.get("Thread-Index")
    msg['To'] = (old_message.get('Reply-To')
                 or old_message.get('From'))
    msg['From'] = constants.REPLY_ADDRESS
    msg['Reply-To'] = constants.REPLY_TO_ADDRESS

    body.attach(MIMEText(new_message, 'html'))
    msg.attach(body)

    return msg.as_string()


def cleanup_tempfiles(partfiles):
    try:
        for fn in partfiles.values():
            os.remove(fn)
    except:
        # if this fails it's fine
        pass
