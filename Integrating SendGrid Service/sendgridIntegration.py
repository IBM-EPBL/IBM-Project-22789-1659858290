import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *


def send_email():
    from_email=Email('211719104041@smartinternz.com')
    to_email=To('jaianish123@gmail.com')
    subject = 'Sendgrid Integrated with flask application'
    content = Content("text/plain", "and easy to do anywhere, even with Python")
    mail = Mail(from_email, to_email, subject, content)
    
    try:
        sg = SendGridAPIClient(['SendGridAPIKEY'])
        response = sg.send(mail)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)
        
send_email()