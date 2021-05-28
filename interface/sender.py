import smtplib
import constants


def send_message(message, user):
    try:
        session = smtplib.SMTP(constants.SMTP_HOST, 587)
        session.ehlo()
        session.starttls()
        session.ehlo()
        session.login(constants.SMTP_USERNAME, constants.SMTP_PASSWORD)
        session.sendmail(constants.REPLY_ADDRESS, [user], message)
        session.quit()
    except Exception as e:
        print(e)
