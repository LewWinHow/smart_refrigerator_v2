import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_refrigerator_v2.settings')
django.setup()
from django.core.mail import EmailMessage
from django.template import loader

from smart_refrigerator_v2.settings import EMAIL_HOST_USER  # 项目配置邮件地址，请参考发送普通邮件部分

def send_email(subject, template, context, recipient_list):
    html_content = loader.render_to_string(
        template,  # 需要渲染的html模板
        context
    )
    msg = EmailMessage(subject, html_content, EMAIL_HOST_USER, recipient_list)
    msg.content_subtype = "html" # Main content is now text/html
    msg.send()
