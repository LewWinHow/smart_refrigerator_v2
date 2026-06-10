import re

from django.shortcuts import redirect
from jupyter_core.version import pattern

from login_log.models import LoginIP
from user.models import User

from utils.hint_message import hint_message


def verify_ip(request):
    current_ip = request.META.get('REMOTE_ADDR')
    login_info = LoginIP.objects.filter(ip=current_ip).first()
    if login_info:
        if login_info.is_blacklist:
            return hint_message(request, 'Your IP has been blocked!', 'account:login')

    return True


def verify_username(request, username, redirect, id=None):
    pattern = r'[a-z0-9]'

    if not username or len(username) > 150 or not re.match(pattern, username):
        return hint_message(request, 'Invalid username!', redirect, id)
    return True


def verify_password(request, password, redirect, id=None):
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9\s])[^\s]+'

    if not password or len(password) < 8 or len(password) > 128 or not re.match(pattern, password):
        return hint_message(request, 'Invalid password!', redirect, id)
    return True


def verify_password_match(request, password, confirm_password, redirect, id=None):
    if password != confirm_password:
        return hint_message(request, 'Passwords do not match!', redirect, id)

    return True


def verify_first_last_name(request, first_name, last_name, redirect, id=None):
    if not first_name or not last_name or len(first_name) > 150 or len(last_name) > 150:
        return hint_message(request, 'Invalid first and last name!', redirect, id)

    return True


def verify_phone(request, phone, redirect, id=None):
    pattern = r'^[1-9][0-9]{7,14}$'
    if phone is not None and not re.match(pattern, phone):
        return hint_message(request, 'Invalid phone!', redirect, id)

    return True


def verify_user_exists(request, username, email, phone, redirect, id=None):
    if id is None:
        if User.objects.filter(username=username).exists():
            return hint_message(request, 'Username already exists!', redirect, id)
        elif User.objects.filter(email=email).exists():
            return hint_message(request, 'Email already exists!', redirect, id)
        elif User.objects.filter(phone=phone, phone__isnull=False).exists():
            return hint_message(request, 'Phone already exists!', redirect, id)
    else:
        if User.objects.filter(username=username).exclude(id=id).exists():
            return hint_message(request, 'Username already exists!', redirect, id)
        elif User.objects.filter(email=email).exclude(id=id).exists():
            return hint_message(request, 'Email already exists!', redirect, id)
        elif User.objects.filter(phone=phone, phone__isnull=False).exclude(id=id).exists():
            return hint_message(request, 'Phone already exists!', redirect, id)

    return True


def verify_image(request, image, redirect, id=None):
    if not image or not image.content_type.startswith('image/') or image.size > 100 * 1024 * 1024:
        return hint_message(request, 'Invalid file!', redirect, id)

    return True


def verify_email(request, email, redirect, id=None):
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

    if not email or not re.match(pattern, email):
        return hint_message(request, 'Invalid email!', redirect, id)

    return True


def verify_superuser(user):
    if not user.is_superuser:
        return redirect('account:login')

    return True
