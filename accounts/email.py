import sendgrid
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *
import os

TEMPLATES = {
    'CONFIRM_ACCOUNT_EMAIL' : 'd-90ec8e5c0213416bb35faaf9597cb800',
    'RESET_PASSWORD_EMAIL' : 'd-9b23556188f144a7a4ce97ba38dc334a'
}

def sendjoiningconfirmation(url,emailad,name,template):
    f = settings.ADMIN_SMTP
    t = emailad
    mail = Mail(from_email=f, to_emails=t)
    mail.template_id = TEMPLATES[template]
    mail.dynamic_template_data = {
        'confirm_link': url,
        'name' : name
    }
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(mail)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)

def sendpasswordresetemail(url,emailad,name,template):
    f = settings.ADMIN_SMTP
    t = emailad
    mail = Mail(from_email=f,to_emails=t)
    mail.template_id = TEMPLATES[template]
    mail.dynamic_template_data = {
        'reset_link': url,
        'name':name
    }
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(mail)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)

def sendcontactmessage(message,subject):
    f = settings.ADMIN_SMTP
    t = 'cbri4nt@gmail.com'
    s = subject
    c = "<html><head><title>Reset Password</title></head><body><p> "+ \
                                    message + "</p></body></html>"
    mail = Mail(from_email=f, subject=s, to_emails=t, html_content=c)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(mail)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)
