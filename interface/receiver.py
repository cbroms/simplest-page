import email
from email import policy
from email.parser import BytesParser
import mimetypes
import ssl
import certifi
import tempfile
import threading
import os
import constants
from imapclient import IMAPClient

ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED


def decode_message(message):
    richest = message.get_body()
    partfiles = {}
    body = ""

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

    # with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    #     # The magic_html_parser has to rewrite the href="cid:...." attributes to
    #     # point to the filenames in partfiles.  It also has to do a safety-sanitize
    #     # of the html.  It could be written using html.parser.
    #     f.write(magic_html_parser(body.get_content(), partfiles))
    # webbrowser.open(f.name)
    # os.remove(f.name)
    print(partfiles)
    # for fn in partfiles.values():
    #     os.remove(fn)


def fetch_and_decode_messages(messages):
    server = IMAPClient(constants.IMAP_HOST, ssl_context=ssl_context)
    server.login(constants.IMAP_USERNAME, constants.IMAP_PASSWORD)
    server.select_folder("INBOX")

    print("fetching messages: {}".format(messages))
    for uid, message_data in server.fetch(messages, "RFC822").items():
        email_message = email.message_from_bytes(message_data[b"RFC822"])
        print(uid, email_message.get("From"), email_message.get(
            "Subject"))
        # print(email_message)

    server.logout()


def decode_test_message():
    server = IMAPClient(constants.IMAP_HOST, ssl_context=ssl_context)
    server.login(constants.IMAP_USERNAME, constants.IMAP_PASSWORD)
    server.select_folder("INBOX")

    for uid, message_data in server.fetch([17], "RFC822").items():
        email_message = email.message_from_bytes(message_data[b"RFC822"])
        print(uid, email_message.get("From"), email_message.get(
            "Subject"))
        msg = BytesParser(policy=policy.default).parsebytes(
            message_data[b"RFC822"])
        decode_message(msg)

    server.logout()


decode_test_message()
# server = IMAPClient(constants.IMAP_HOST, ssl_context=ssl_context)
# server.login(constants.IMAP_USERNAME, constants.IMAP_PASSWORD)
# server.select_folder("INBOX")


# # Start IDLE mode
# server.idle()
# print("Connection is now in IDLE mode, send yourself an email or quit with ^c")

# while True:
#     try:
#         # Wait for up to 30 seconds for an IDLE response
#         responses = server.idle_check(timeout=30)
#         # print("Server sent:", responses if responses else "nothing")

#         for uid, tag in responses:
#             # check if we got any new mail. if so, the response should look like
#             # [(uuid, b'EXISTS'), (num_recent, b'RECENT')]
#             if tag == b'EXISTS':
#                 fetch_task = threading.Thread(
#                     target=fetch_and_decode_messages, args=([uid],))
#                 fetch_task.start()

#     except KeyboardInterrupt:
#         break


# server.idle_done()
# print("\nIDLE mode done")
# server.logout()
