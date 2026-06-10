import os
import django
from django.utils import timezone
from django.core.mail import EmailMessage
from django.conf import settings

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_refrigerator_v2.settings')
django.setup()

from item.models import Item

EXPIRATION_DAYS = {
        'apple':14,
        'orange':14,
        'banana':3,
        'carrot':14,
        'tomato':5,
        'Egg':3,
        'chicken':0.,
        '7up':180,
        'coca':180,
        'fanta':180,
        'pepsi':180,
        'redbull':180,
        'stingray':180,
}

NEAR_EXPIRE_THRESHOLD = 3
RECIPIENT_EMAIL = 'xiaohao6070@gmail.com'


def check_expired_items():
    now = timezone.now()

    expired_items = []
    near_expire_items = []

    for item in Item.objects.all():
        name = item.item
        if name not in EXPIRATION_DAYS:
            continue

        expiration_days = EXPIRATION_DAYS[name]
        age_days = (now - item.record_time).days
        remaining_days = expiration_days - age_days

        if remaining_days < 0:
            expired_items.append((item, -remaining_days))
        elif remaining_days <= NEAR_EXPIRE_THRESHOLD:
            near_expire_items.append((item, remaining_days))

    if not expired_items and not near_expire_items:
        print("No expired or near-expired ingredients.")
        return

    subject = "[SmartFace-Fridge] - Some items are nearing or have expired!"
    body = ""

    if near_expire_items:
        body += "The following items are nearing their expiration dates:\n\n"
        for item, days_left in near_expire_items:
            body += (
                f"Item: {item.item}\n"
                f"Record Time: {item.record_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Remaining days: {days_left} days\n\n"
            )

    if expired_items:
        body += "The following items have expired:\n\n"
        for item, days_over in expired_items:
            body += (
                f"Item: {item.item}\n"
                f"Record Time: {item.record_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Expired by: {days_over} days\n\n"
            )

    email = EmailMessage(subject, body, to=[RECIPIENT_EMAIL])

    # Attachment (image)
    for item_group in (near_expire_items, expired_items):
        for item, _ in item_group:
            if item.image:
                image_path = os.path.join(settings.MEDIA_ROOT, item.image.name)
                if os.path.exists(image_path):
                    email.attach_file(image_path)

    email.send()
    print("Reminder email sent.")




if __name__ == '__main__':
    check_expired_items()


