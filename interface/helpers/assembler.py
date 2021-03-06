import tempfile
import os
import constants
from email.utils import parsedate_tz, mktime_tz
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

    description = parser.description.replace('\n', '').replace('\r', '')

    return (parser.new_html, parser.image, description)


def html_to_markdown(html):
    return markdownify(html)

def open_and_compile_local_template(type):
    # type can be any of the template types (rn just 'index' or 'page')
    with open("templates/{}.handlebars".format(type), 'r') as file:
        source = file.read()
        # TODO precompile this for efficiency 
        template = compiler.compile(source)
        return template

def assemble_content(attrs, content, partfiles, page_template):
    (new_html, image, description) = replace_cids(content, partfiles)

    page_output = page_template({
        'body': new_html,
        'image': image,
        'description': description,
        **attrs
    })

    # convert the email's formatted date to a UNIX timestamp 
    time = str(mktime_tz(parsedate_tz(attrs['date'])))

    # new_markdown = html_to_markdown(new_html)

    # return the html as well as the attrs that we'll save to the info.json file
    # that's used when rendering the index page in the future
    return [page_output, {'image': image, 'description': description, 'time': time, 'date': attrs['date']}]


def assemble_index(previous_content, index_template):
    index_output = index_template({
        'posts': previous_content,
    })

    return index_output

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
