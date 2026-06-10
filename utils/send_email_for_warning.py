def send_email_for_warning(email, image_path):
    from django.core.mail import EmailMultiAlternatives
    from email.mime.image import MIMEImage

    subject = "[SmartFace-Fridge] - A user has removed your item without permission"
    text_content = "A user has removed your item without permission."
    html_content = """
    <html>
      <body>
        <p>Monitoring Image:</p>
        <img src="cid:my_photo">  <!-- Note: use cid here -->
      </body>
    </html>
    """

    msg = EmailMultiAlternatives(subject, text_content, 'xiaohao6070@gmail.com', [email])
    msg.attach_alternative(html_content, "text/html")

    # Embed image
    with open(image_path, "rb") as f:
        image = MIMEImage(f.read())
        image.add_header("Content-ID", "<my_photo>")  # Corresponds to cid in HTML
        msg.attach(image)

    msg.send()
