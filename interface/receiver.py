import ssl
import certifi
import threading
import email
import constants
from imapclient import IMAPClient

from helpers import deducer, decoder, assembler, modifier

import messages
import sender

ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED


def fetch_and_decode_messages(new_messages):
    server = IMAPClient(constants.IMAP_HOST, ssl_context=ssl_context)
    server.login(constants.IMAP_USERNAME, constants.IMAP_PASSWORD)
    server.select_folder("INBOX")

    for uid, message_data in server.fetch(new_messages, "RFC822").items():
        email_message = email.message_from_bytes(message_data[b"RFC822"])
        user = email_message.get("From")
        receiver = email_message.get("To")
        reply_user = (email_message.get('Reply-To')
                      or email_message.get('From'))
        date = email_message.get("Date")
        subject = email_message.get("Subject")

        intentions = deducer.deduce_intention(user, receiver, subject)

        print("{} received".format(uid))

        if intentions[0][0] == 'post':
            try:
                # decode the message, assemble the files, upload them
                message = decoder.bytes_to_message(message_data)
                content, files = decoder.decode_message(message)
                new_html = assembler.assemble_content(
                    user, subject, date, content, files)
            except Exception as e:
                print(e)
                # something went wrong parsing.
                sender.send_message(assembler.assemble_email(
                    email_message, messages.format_error), reply_user)
                print("{} parse fail".format(uid))
                break

            try:
                post_url = modifier.create_post(subject, new_html, files)
                sender.send_message(assembler.assemble_email(email_message,
                                                             messages.posted, {'url': post_url}), reply_user)
                print("{} posted: {}".format(uid, post_url))
            except:
                # something went wrong posting
                sender.send_message(assembler.assemble_email(
                    email_message, messages.posting_error), reply_user)
                print("{} post fail".format(uid))
                break

            try:
                assembler.cleanup_tempfiles(files)
            except:
                # fine if this fails
                pass

    server.logout()


server = IMAPClient(constants.IMAP_HOST, ssl_context=ssl_context)
server.login(constants.IMAP_USERNAME, constants.IMAP_PASSWORD)
server.select_folder("INBOX")

# Start IDLE mode
server.idle()
print("Connection is now in IDLE mode, send yourself an email or quit with ^c")

while True:
    try:
        # Wait for up to 30 seconds for an IDLE response
        responses = server.idle_check(timeout=30)
        # print("Server sent:", responses if responses else "nothing")

        if responses:
            try:
                for uid, tag in responses:
                    # check if we got any new mail. if so, the response should look like
                    # [(uuid, b'EXISTS'), (num_recent, b'RECENT')]
                    if tag == b'EXISTS':
                        fetch_task = threading.Thread(
                            target=fetch_and_decode_messages, args=([uid],))
                        fetch_task.start()
            except:
                # this fails when a message is fetched and marked as "seen"
                pass

    except KeyboardInterrupt:
        break


server.idle_done()
print("\nIDLE mode done")
server.logout()
