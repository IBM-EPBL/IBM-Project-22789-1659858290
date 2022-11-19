import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_Email():
    from_email=Email('211719104044@smartinternz.com')
    to_email=To('hayathbasha.a.2019.cse@ritchennai.edu.in')
    subject = 'EXPENSE LIMIT EXCEEDED'
    content = Content("text/plain", "You have exceeded your MONTHLY EXPENSE LIMIT\nwith regards\n\t\t PETA-Team")
    mail = Mail(from_email, to_email, subject, content)
    
    try:
        sg = SendGridAPIClient('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')
        response = sg.send(mail)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)