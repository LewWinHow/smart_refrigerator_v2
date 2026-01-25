import os
import django
from django.utils import timezone
from django.core.mail import EmailMessage
from django.conf import settings

# 初始化 Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_refrigerator_v2.settings')
django.setup()

from item.models import Item

EXPIRATION_DAYS = {
        'apple':14,
        'orange':14,
        'banana':3,
        'carrot':14,
        'tomato':5,
        'egg':3,
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
        print("没有过期或临近过期的食材。")
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

    # 附件（图片）
    for item_group in (near_expire_items, expired_items):
        for item, _ in item_group:
            if item.image:
                image_path = os.path.join(settings.MEDIA_ROOT, item.image.name)
                if os.path.exists(image_path):
                    email.attach_file(image_path)

    email.send()
    print("提醒邮件已发送。")




if __name__ == '__main__':
    check_expired_items()
# EXPIRATION_DAYS = {
#     'apple':14,
#     'orange':14,
#     'banana':3,
#     'carrot':14,
#     'tomato':5,
#     'egg':3,
#     'chicken':0.,
#     '7up':180,
#     'coca':180,
#     'fanta':180,
#     'pepsi':180,
#     'redbull':180,
#     'stingray':180,
# }
#
# NEAR_EXPIRE_THRESHOLD = 3
# def expire_items():
#     now = datetime.datetime.now()
#     expire_item_list = []
#     near_expire_item_list = []
#
#     for item in Item.objects.all():
#
#         if item.item not in EXPIRATION_DAYS:
#             continue
#
#         expiration_days = EXPIRATION_DAYS[item.item]
#         age_days = (now - item.record_time).days
#         remaining_days = expiration_days - age_days
#
#         if remaining_days < 0:
#             expire_item = {'item': item.item, 'remaining_days': remaining_days, 'image':item.image}
#             expire_item_list.append(expire_item)
#         elif remaining_days <= NEAR_EXPIRE_THRESHOLD:
#             near_expire_item = {'item': item.item, 'remaining_days': remaining_days, 'image':item.image}
#             near_expire_item_list.append(near_expire_item)
#
#     if not expire_item_list and not near_expire_item_list:
#         print("没有过期或临近过期的食材。")
#         return
#
#     context = {
#         'expire_item_list': expire_item_list,
#         'near_expire_item_list': near_expire_item_list,
#     }
#
#     return context
#
# while True:
#     context = expire_items()
#     if context:
#         send_email('Item Expiry Notification', r'C:\Users\xiaoh\Downloads\smart_refrigerator_v2 - Copy - Copy\templates\item_expire_email.html',
#                    context,['xiaohao6070@gmail.com'])


