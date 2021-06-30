import ssl
import certifi
import threading
import email
import time
import constants
from imapclient import IMAPClient

from helpers import deducer, decoder, assembler, interfacer

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

        if intentions[0][0] == 'page':
            try:
                # decode the message, assemble the files, upload them
                message = decoder.bytes_to_message(message_data)
                content, files = decoder.decode_message(message)
                new_html = assembler.assemble_content(
                    user, subject, date, content, files)
            except Exception as e:
                # print(e)
                # something went wrong parsing.
                sender.send_message(assembler.assemble_email(
                    email_message, messages.format_error), reply_user)
                print("{} parse fail".format(uid))
                break

            try:
                post_url = interfacer.create_post(user, subject, new_html, files)
                sender.send_message(assembler.assemble_email(email_message,
                                                             messages.posted, {'url': post_url}), reply_user)
                print("{} posted: {}".format(uid, post_url))
            except:
                # something went wrong posting
                sender.send_message(assembler.assemble_email(
                    email_message, messages.system_error), reply_user)
                print("{} post fail".format(uid))
                break

            try:
                assembler.cleanup_tempfiles(files)
            except:
                # fine if this fails
                pass
        elif intentions[0][0] == 'manage':
            try: 
                # if this returns None, the user doesn't have permission to edit 
                metadata = interfacer.get_site_metadata(subject, user)
                if metadata != None: 
                    # if the site doesn't already exist, create it 
                    if metadata['new']:
                        interfacer.create_site(metadata)
                    # create a new settings session 
                    url = interfacer.create_session_url(metadata)
                    sender.send_message(assembler.assemble_email(email_message, messages.session_created, {'url': url}), reply_user)
                    print("{} settings session created".format(uid))

                else:
                    sender.send_message(assembler.assemble_email(email_message, messages.permission_error, {'sitename': subject}), reply_user)
                    print("{} settings permission denied".format(uid))
            except Exception as e:
                # print(e)
                sender.send_message(assembler.assemble_email(
                    email_message, messages.system_error), reply_user)
                print("{} settings fail".format(uid))

    server.logout()


server = IMAPClient(constants.IMAP_HOST, ssl_context=ssl_context)
server.login(constants.IMAP_USERNAME, constants.IMAP_PASSWORD)
server.select_folder("INBOX")

# Start IDLE mode
while True:
    try:
        print("starting IDLE mode")
        server.idle()
        start_time = time.time()
        current_time = start_time

        # restart after 10 mins
        while int(current_time - start_time) < 600:
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

                current_time = time.time()

            except KeyboardInterrupt as e:
                raise e

        server.idle_done()
        print("\nIDLE mode done")

    except KeyboardInterrupt:
        break


server.logout()
