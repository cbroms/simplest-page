
import ssl
import certifi
import threading
import os
import email
import constants
from imapclient import IMAPClient

from helpers import deducer, decoder, assembler, modifier

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

    for uid, message_data in server.fetch([19], "RFC822").items():
        email_message = email.message_from_bytes(message_data[b"RFC822"])
        user = email_message.get("From")
        subject = email_message.get("Subject")

        intentions = deducer.deduce_intention(
            user, email_message.get("To"), subject)

        for intention, arg in intentions:

            if intention == 'newsite':

                site_is_taken = modifier.get_site(arg) == None
                if not site_is_taken:
                    # the subject is the site title, body is the description
                    modifier.create_site(arg, user, subject)

            elif intention == 'postto':

                site = modifier.get_site(arg)
                if site == None:
                    # FAIL: the site doesn't exist
                    break
                if site['user'] != user:
                    # FAIL: this user doesn't have permission to post
                    break

                message = decoder.bytes_to_message(message_data)
                content, files = decoder.decode_message(message)
                new_html = assembler.assemble_content(content, files)
                modifier.create_post(site, subject, new_html, files)
                assembler.cleanup_tempfiles(files)

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
