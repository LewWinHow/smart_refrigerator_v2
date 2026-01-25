def send_email_for_warning(email, image_path):
    from django.core.mail import EmailMultiAlternatives
    from email.mime.image import MIMEImage

    subject = "[SmartFace-Fridge] - A user has removed your item without permission"
    text_content = "A user has removed your item without permission."
    html_content = """
    <html>
      <body>
        <p>Monitoring Image:</p>
        <img src="cid:my_photo">  <!-- 注意这里用 cid -->
      </body>
    </html>
    """

    msg = EmailMultiAlternatives(subject, text_content, 'xiaohao6070@gmail.com', [email])
    msg.attach_alternative(html_content, "text/html")

    # 嵌入图片
    with open(image_path, "rb") as f:
        image = MIMEImage(f.read())
        image.add_header("Content-ID", "<my_photo>")  # 与 HTML 中的 cid 对应
        msg.attach(image)

    msg.send()
