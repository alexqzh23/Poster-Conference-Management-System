from django.core.mail import send_mail


@app.task(name='celery_send_email_code')
def celery_send_email_code(subject, from_email, recipient_list, html_message):
    try:
        send_mail(subject=subject, message='', from_email=from_email, recipient_list=recipient_list,
                  html_message=html_message)
    except Exception as e:
        print('邮件发送失败', e)
