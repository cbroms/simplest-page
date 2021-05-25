import os
import mimetypes
import tempfile

from email import policy
from email.parser import BytesParser


def bytes_to_message(bytes):
    return BytesParser(policy=policy.default).parsebytes(
        bytes[b"RFC822"])


def decode_message(message):
    richest = message.get_body()
    partfiles = {}

    body = richest.get_body(preferencelist=('html'))
    for part in richest.iter_attachments():
        fn = part.get_filename()
        if fn:
            extension = os.path.splitext(part.get_filename())[1]
        else:
            extension = mimetypes.guess_extension(part.get_content_type())
        with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as f:
            f.write(part.get_content())
            # again strip the <> to go from email form of cid to html form.
            partfiles[part['content-id'][1:-1]] = f.name

    return (body.get_content(),  partfiles)
