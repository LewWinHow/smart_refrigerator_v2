import random
import string
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.views import View

from login_log.models import LoginRecord
from user.models import FaceID
from utils.get_data import get_device_info
from utils.get_face_embedding import get_face_embedding
from utils.save_profile_image import save_profile_image
from utils.send_email import send_email
from utils.verify import *


class Login(View):

    def get(self, request):
        return render(request, 'account/login.html')

    def post(self, request):
        ip = request.META.get('REMOTE_ADDR')
        device_info = get_device_info(request)
        system = device_info['system']
        device = device_info['device']
        is_bot = device_info['is_bot']

        login_ip = LoginIP.objects.filter(ip=ip).first()
        if login_ip:
            if is_bot:
                login_ip.is_blacklist = 1
                login_ip.save()
        else:
            if is_bot:
                login_ip = LoginIP(
                    ip=ip,
                    system=system,
                    device=device,
                    is_bot=is_bot,
                    blacklist=1,
                )
            else:
                login_ip = LoginIP(
                    ip=ip,
                    system=system,
                    device=device,
                    is_bot=is_bot,
                )
            login_ip.save()

        username = request.POST.get('username') or None

        if verify_username(request, username, 'account:login') is not True:
            return verify_username(request, username, 'account:login')

        password = request.POST.get('password') or None

        if verify_password(request, password, 'account:login') is not True:
            return verify_password(request, password, 'account:login')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            login_ip.failed_count = 0
            login_ip.save()
            login_record = LoginRecord(
                login_ip=login_ip,
                username=username,
                password=password,
                status=1,
                record_time=datetime.now(),
            )
            login_record.save()
            return hint_message(
                request, 'Login successful!', 'monitoring:get_monitoring_display_and_detect_data'
            )
        else:
            login_ip.failed_count += 1
            login_ip.save()
            if login_ip.failed_count > 5:
                login_ip.is_blacklist = 1
                login_ip.save()

            login_record = LoginRecord(
                login_ip=login_ip,
                username=username,
                password=password,
                status=0,
                record_time=datetime.now(),
            )
            login_record.save()
            return hint_message(
                request, 'Login failed! Invalid username or password.', 'account:login'
            )


class ForgotPassword(View):
    def get(self, request):
        return render(request, 'account/forgot_password.html')

    def post(self, request):
        email = request.POST.get('email') or None
        if verify_email(request, email, 'account:forgot_password') is not True:
            return verify_email(request, email, 'account:forgot_password')

        user = User.objects.filter(email=email).first()
        if not user:
            return hint_message(
                request, 'Email does not exist!', 'account:forgot_password'
            )

        captcha_input = request.POST.get('captcha') or None
        captcha_generate = request.session.get('captcha') or None

        if captcha_input == captcha_generate and captcha_input is not None and captcha_generate is not None:
            verification_code = ''.join(
                random.choices(string.ascii_letters + string.digits, k=6)
            )
            request.session['email'] = email
            request.session['verification_code'] = verification_code

            context = {'verification_code': verification_code}
            send_email('Verification Code',
                       r'C:\Users\xiaoh\Downloads\smart_refrigerator - Copy\templates\verification_code_email.html',
                       context,
                       [email])

            return hint_message(
                request,
                'The verification code has been sent to your email. Please check!',
                'account:verification_code',
            )
        else:
            return hint_message(
                request, 'Captcha incorrect!', 'account:forgot_password'
            )


class VerificationCode(View):
    def get(self, request):
        email = request.session.get('email') or None
        verification_code = request.session.get('verification_code') or None
        if not email or not verification_code:
            return redirect('account:login')
        return render(request, 'account/verification_code.html')

    def post(self, request):
        verification_code = request.POST.get('verification_code') or None
        verification_code_generate = request.session.get('verification_code')
        if verification_code == verification_code_generate:
            request.session['reset_password'] = True
            return hint_message(
                request, 'Verification code correct!', 'account:reset_password'
            )
        else:
            return hint_message(
                request, 'Verification code incorrect!', 'account:verification_code'
            )


class ResetPassword(View):
    def get(self, request):
        email = request.session.get('email') or None
        reset_password = request.session.get('reset_password') or None
        if not email or not reset_password:
            return redirect('account:login')
        return render(request, 'account/reset_password.html')

    def post(self, request):
        email = request.session.get('email')
        new_password = request.POST.get('new_password') or None
        if verify_password(request, new_password, 'account:reset_password') is not True:
            return verify_password(request, new_password, 'account:reset_password')

        confirm_password = request.POST.get('confirm_password') or None
        if verify_password(request, confirm_password, 'account:reset_password') is not True:
            return verify_password(request, confirm_password, 'account:reset_password')

        if verify_password_match(request, new_password, confirm_password, 'account:reset_password') is not True:
            return verify_password(request, new_password, 'account:reset_password')

        user = User.objects.filter(email=email).first()
        user.set_password(new_password)
        user.save()

        request.session['email'] = None
        request.session['request'] = None
        request.session['verification_code'] = None
        request.session['reset_password'] = None
        return hint_message(request, 'Reset Password Successful!', 'account:login')


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('account:login')


class Register(View):
    def get(self, request):
        return render(request, 'user/register_add_edit_info_user.html', {'page': 'register'})

    def post(self, request):
        username = request.POST.get('username') or None
        if verify_username(request, username, 'account:register') is not True:
            return verify_username(request, username, 'account:register')

        password = request.POST.get('password') or None
        if verify_password(request, password, 'account:register') is not True:
            return verify_password(request, password, 'account:register')

        confirm_password = request.POST.get('confirm_password') or None
        if verify_password(request, confirm_password, 'account:register') is not True:
            return verify_password(request, password, 'account:register')

        if verify_password_match(request, password, confirm_password, 'account:register') is not True:
            return verify_password_match(request, password, confirm_password, 'account:register')

        first_name = request.POST.get('first_name') or None
        last_name = request.POST.get('last_name') or None
        if verify_first_last_name(request, first_name, last_name, 'account:register') is not True:
            return verify_first_last_name(request, first_name, last_name, 'account:register')

        birthday = request.POST.get('birthday') or None
        gender = request.POST.get('gender') or None
        phone = request.POST.get('phone') or None

        if verify_phone(request, phone, 'account:register') is not True:
            return verify_phone(request, phone, 'account:register')

        email = request.POST.get('email') or None
        if verify_email(request, email, 'account:register') is not True:
            return verify_email(request, email, 'account:register')

        if verify_user_exists(request, username, email, phone, 'account:register') is not True:
            return verify_user_exists(request, username, email, phone, 'account:register')

        profile_image = request.FILES.get('profile_image')
        if verify_image(request, profile_image, 'account:register') is not True:
            return verify_image(request, profile_image, 'account:register')

        face_embedding = get_face_embedding(profile_image)

        if face_embedding is None:
            hint_message(request, 'Invalid profile image!', 'account:register')

        image_path = save_profile_image(profile_image, 'profile_image')

        user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            birthday=birthday,
            gender=gender,
            phone=phone,
            email=email,
            is_superuser=False,
            is_staff=False,
            is_active=True,
            profile_image=image_path
        )

        face_id = FaceID(embedding=face_embedding, user_id=user.id)
        face_id.set_embedding(face_embedding)

        user.set_password(password)
        user.save()
        face_id.save()

        return hint_message(request, 'Register successful!', 'account:login')


class GetCaptcha(View):
    def get(self, request):
        # 1. 生成随机验证码
        chars = string.ascii_uppercase + string.digits
        captcha_text = ''.join(random.choice(chars) for _ in range(4))

        # 2. 存入 session（用于校验）
        request.session['captcha'] = captcha_text

        # 3. 创建图片
        width, height = 120, 40
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)

        # 字体（Windows 可以用这个）
        font = ImageFont.truetype('arial.ttf', 28)

        # 4. 绘制验证码文字
        for i, char in enumerate(captcha_text):
            draw.text((10 + i * 25, 5), char, font=font, fill='black')

        # 5. 干扰线
        for _ in range(5):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line((x1, y1, x2, y2), fill='gray')

        # 6. 返回图片
        from io import BytesIO
        buffer = BytesIO()
        image.save(buffer, 'PNG')
        buffer.seek(0)

        return HttpResponse(buffer, content_type='image/png')
