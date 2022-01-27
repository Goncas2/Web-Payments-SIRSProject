import smtplib
from getpass import getpass


def sendEmail(email, url, store_name, amount):
    try:
        
        bank_email = "sirs.alameda08@gmail.com"
        bank_pass="sirsisnice123"

        sent_from = bank_email

        to = []
        to.append(email)

        text = "Store:"+ store_name + "\n" + "Amount:" + str(amount) + "\n" + "Click here to confirm or cancel: " + url
        subject = 'Confirm transaction'
        email_text = """\
        From: %s
        To: %s
        Subject: %s

        %s
        """ % (sent_from, ", ".join(to), subject, text)


        #Create your SMTP session
        smtp = smtplib.SMTP('smtp.gmail.com', 587)

        smtp.ehlo()
        #Use TLS to add security
        smtp.starttls()
        smtp.ehlo()

        #User Authentication
        smtp.login(bank_email,bank_pass)

        #Sending the Email
        smtp.sendmail(bank_email, email, email_text)

        #Terminating the session
        smtp.quit()
        return True

    except Exception as ex:
        print ("Something went wrong while sending email",ex)
        return None

