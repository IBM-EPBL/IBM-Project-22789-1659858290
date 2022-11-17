import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

message= Mail(from_email='211719104041@smartinternz.com',
                 to_emails='hayathbasha8888@gmail.com',
                 subject='ibmproject',
                 content='personal expense tracker'
                 )

try:
    sg= SendGridAPIClient('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')
    response= sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)

except Exception as e:
    print(e.message)
    

