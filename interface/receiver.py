import constants
import email
from imapclient import IMAPClient


server = IMAPClient(constants.IMAP_HOST)
server.login(constants.IMAP_USERNAME, constants.IMAP_PASSWORD)
server.select_folder("INBOX")

def get_unseen_mail():
    """
    find any unseen messages, download them, and parse their content
    this will make them as seen on the server, so it will only work 
    once with new emails
    """
    print("getting new")
    messages = server.search("UNSEEN")
    for uid, message_data in server.fetch(messages, "RFC822").items():
        email_message = email.message_from_bytes(message_data[b"RFC822"])
        print(uid, email_message.get("From"), email_message.get("Subject"), email_message.get("Body"))


# Start IDLE mode
server.idle()
print("Connection is now in IDLE mode, send yourself an email or quit with ^c")

while True:
    try:
        # Wait for up to 30 seconds for an IDLE response
        responses = server.idle_check(timeout=30)
        print("Server sent:", responses if responses else "nothing")
        # check if we got any new mail. if so, the response should look like
        # [(uuid, b'EXISTS'), (num_recent, b'RECENT')]
        num_new, res =  responses[len(responses) - 1]
        print(num_new, res)
        if res == b'RECENT':
            get_unseen_mail()

    except KeyboardInterrupt:
        break

server.idle_done()
print("\nIDLE mode done")
server.logout()


