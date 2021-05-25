
from interface.helpers.assembler import assemble_file
import ssl
import certifi
import threading
import os
import constants
from imapclient import IMAPClient

from helpers import decoder, assembler, uploader

ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED


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
        # email_message = email.message_from_bytes(message_data[b"RFC822"])
        # print(uid, email_message.get("From"), email_message.get(
        #     "Subject"))
        message = decoder.bytes_to_message(message_data)
        content, files = decoder.decode_message(message)
        new_html_file = assembler.assemble_file(content, files)
        # new_filename = assembler.create_new_filename()
        # response = uploader.upload_file(new_html_file, new_filename)
        assembler.cleanup_tempfiles(new_html_file, files)

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
