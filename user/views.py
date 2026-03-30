import uuid

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.core.validators import validate_email
from django.db.models import Q
from django.shortcuts import render
from django.views import View

from item.models import Item
from user.models import FaceID
from monitoring.models import MonitoringRecord
from utils.get_data import get_data_by_page
from utils.save_profile_image import save_profile_image
from utils.verify import *
from utils.get_face_embedding import get_face_embedding
from utils.delete_image import delete_single_image


class UserList(LoginRequiredMixin, View):

    def get(self, request, page=1):

        user = request.user
        is_superuser = user.is_superuser

        if verify_superuser(user) is not True:
            return verify_superuser(user)

        user_list = User.objects.all().order_by('-id')
        user_list = get_data_by_page(user_list, page)[0]
        is_paginated = get_data_by_page(user_list, page)[1]
        return render(request, 'user/user_list.html',
                      {'is_superuser': is_superuser, 'user_list': user_list, 'is_paginated': is_paginated,'order_by':'0'})

    def post(self, request, page=1):

        user = request.user
        is_superuser = user.is_superuser
        if verify_superuser(user) is not True:
            return verify_superuser(user)

        filter_select = request.POST.get('filter_select') or None
        print(filter_select)
        filter_input = request.POST.get('filter_input') or None
        print(filter_input)
        filter_input_second = request.POST.get('filter_input_second') or None
        gender_select = request.POST.get('gender_select') or None
        supervisor_select = request.POST.get('supervisor_select') or None
        staff_select = request.POST.get('staff_select') or None
        status_select = request.POST.get('status_select') or None
        user_list = User.objects.all()
        order_by = request.POST.get('order_by') or None

        if filter_select:
            if filter_select == '1':
                user_list = User.objects.all()
            elif filter_select == '2':
                if filter_input:
                    user_list = User.objects.filter(id=filter_input).all()
            elif filter_select == '3':
                if filter_input:
                    user_list = User.objects.filter(username__contains=filter_input).all()
            elif filter_select == '4':
                if filter_input:
                    full_name = filter_input.strip().split()
                    if len(full_name) == 1:
                        Q(first_name__icontains=full_name[0]) | Q(last_name__icontains=full_name[0])
                    elif len(filter_input) >= 2:
                        Q(first_name__icontains=full_name[0]) | Q(last_name__icontains=full_name[-1])
            elif filter_select == '5':
                if gender_select:
                    if gender_select == '0':
                        user_list = User.objects.filter(gender=None).all()
                    else:
                        user_list = User.objects.filter(gender=gender_select).all()
            elif filter_select == '6':
                if supervisor_select:
                    user_list = User.objects.filter(is_superuser=supervisor_select).all()
            elif filter_select == '7':
                if staff_select:
                    user_list = User.objects.filter(is_staff=staff_select).all()
            elif filter_select == '8':
                if status_select:
                    user_list = User.objects.filter(is_active=status_select).all()
            elif filter_select == '9':
                if filter_input and filter_input_second:
                    user_list = User.objects.filter(date_joined__gte=filter_input,
                                                    date_joined__lte=filter_input_second).all()
                elif filter_input and filter_input_second is None:
                    user_list = User.objects.filter(date_joined__gte=filter_input).all()
                elif filter_input is None and filter_input_second:
                    user_list = User.objects.filter(
                        date_joined__lte=filter_input_second).all()

        if order_by and order_by == '1':
            user_list = user_list.order_by('id')
        else:
            user_list = user_list.order_by('-id')

        user_list = get_data_by_page(user_list, page)[0]
        is_paginated = get_data_by_page(user_list, page)[1]
        return render(request, 'user/user_list.html',
                      {'user_list': user_list,
                       'is_paginated': is_paginated, 'filter_select': filter_select, 'filter_input': filter_input,
                       'filter_input_second': filter_input_second, 'gender_select': gender_select,
                       'supervisor_select': supervisor_select, 'staff_select': staff_select,
                       'status_select': status_select,
                       'order_by': order_by, 'is_superuser': is_superuser, })


class AddUser(LoginRequiredMixin, View):

    def get(self, request):

        user = request.user
        if verify_superuser(user) is not True:
            return verify_superuser(user)

        return render(request, 'user/register_add_edit_info_user.html', {'page': 'add_user'})

    def post(self, request):

        user = request.user
        if verify_superuser(user) is not True:
            return verify_superuser(user)

        username = request.POST.get('username') or None
        if verify_username(request, username, 'user:add_user') is not True:
            return verify_username(request, username, 'user:add_user')

        password = request.POST.get('password') or None
        confirm_password = request.POST.get('confirm_password') or None

        if verify_password(request, password, 'user:add_user') is not True:
            return verify_password(request, password, 'user:add_user')

        if verify_password(request, confirm_password, 'user:add_user') is not True:
            return verify_password(request, confirm_password, 'user:add_user')

        first_name = request.POST.get('first_name') or None
        last_name = request.POST.get('last_name') or None
        if verify_first_last_name(request, first_name, last_name, 'user:add_user') is not True:
            return verify_first_last_name(request, first_name, last_name, 'user:add_user')

        birthday = request.POST.get('birthday') or None
        gender = request.POST.get('gender') or None
        phone = request.POST.get('phone') or None

        if verify_phone(request, phone, 'user:add_user') is not True:
            return verify_phone(request, phone, 'user:add_user')

        if phone:
            if phone[0] != '6':
                phone = '6' + phone

        email = request.POST.get('email') or None

        if verify_email(request, email, 'user:add_user') is not True:
            return verify_email(request, email, 'user:add_user')

        if verify_user_exists(request, username, email, phone, 'user:add_user') is not True:
            return verify_user_exists(request, username, email, phone, 'user:add_user')

        is_superuser = request.POST.get('is_superuser') or None
        is_staff = request.POST.get('is_staff') or None
        is_active = request.POST.get('is_active') or None

        profile_image = request.FILES.get('profile_image')

        if verify_image(request, profile_image, 'user:add_user') is not True:
            return verify_image(request, profile_image, 'user:add_user')

        face_embedding = get_face_embedding(profile_image)
        if face_embedding is None:
            return hint_message(request, 'Invalid profile image.', 'user:add_user')

        image_path = save_profile_image(profile_image, 'profile_image')

        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            birthday=birthday,
            gender=gender,
            phone=phone,
            email=email,
            is_superuser=is_superuser,
            is_staff=is_staff,
            is_active=is_active,
            profile_image=image_path,
        )

        user.set_password(password)
        user.save()
        face_identity = FaceID(user_id=user.id)
        face_identity.set_embedding(face_embedding)
        face_identity.save()
        return hint_message(request, 'Add successful!', 'user:user_list')


class DeleteUser(LoginRequiredMixin, View):

    def get(self, request, id):

        user = request.user

        if verify_superuser(user) is not True:
            return verify_superuser(user)

        user = User.objects.filter(id=id).first()
        face_identity = FaceID.objects.filter(user_id=id).first()

        if not user:
            return hint_message(request, 'User not found.', 'user:user_list')

        profile_image = user.profile_image.name.split('/')[-1]
        delete_single_image(profile_image, 'profile_image')

        if face_identity:
            face_identity.delete()

        user.delete()
        return redirect('user:user_list')


class SetUserStatus(LoginRequiredMixin, View):

    def get(self, request, id):

        user = request.user
        if verify_superuser(user) is not True:
            return verify_superuser(user)

        user = User.objects.filter(id=id).first()

        if not user:
            return hint_message(request, 'User not found.', 'user:user_list')

        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True

        user.save()
        return redirect('user:user_list')


class EditUser(LoginRequiredMixin, View):

    def get(self, request, id):

        user = request.user
        if verify_superuser(user) is not True:
            return verify_superuser(user)

        user = User.objects.filter(id=id).first()

        if not user:
            return hint_message(request, 'User not found.', 'user:user_list')

        return render(request, 'user/register_add_edit_info_user.html',
                      {'page': 'edit_user', 'user': user})

    def post(self, request, id):

        user = request.user
        if verify_superuser(user) is not True:
            return verify_superuser(user)

        user = User.objects.filter(id=id).first()

        if not user:
            return hint_message(request, 'User not found.', 'user:user_list')

        old_username = user.username
        old_profile_image = user.profile_image.name.split('/')[-1]

        username = request.POST.get('username') or None
        if verify_username(request, username, 'user:edit_user') is not True:
            return verify_username(request, username, 'user:edit_user')

        password = request.POST.get('password') or None

        confirm_password = request.POST.get('confirm_password') or None

        if password is not None and confirm_password is not None:
            if verify_password(request, password, 'user:add_user') is not True:
                return verify_password(request, password, 'user:add_user')

            if verify_password(request, confirm_password, 'user:add_user') is not True:
                return verify_password(request, confirm_password, 'user:add_user')

        first_name = request.POST.get('first_name') or None
        last_name = request.POST.get('last_name') or None
        if verify_first_last_name(request, first_name, last_name, 'user:edit_user') is not True:
            return verify_first_last_name(request, first_name, last_name, 'user:edit_user')

        birthday = request.POST.get('birthday') or None

        gender = request.POST.get('gender') or None

        phone = request.POST.get('phone') or None

        if verify_phone(request, phone, 'user:edit_user', id) is not True:
            return verify_phone(request, phone, 'user:edit_user', id)

        if phone:
            if phone[0] != '6':
                phone = '6' + phone

        email = request.POST.get('email') or None
        if verify_email(request, email, 'user:edit_user', id) is not True:
            return verify_email(request, email, 'user:edit_user', id)

        if verify_user_exists(request, username, email, phone, 'user:edit_user', id) is not True:
            return verify_user_exists(request, username, email, phone, 'user:edit_user', id)

        is_superuser = request.POST.get('is_superuser') or None
        is_staff = request.POST.get('is_staff') or None
        is_active = request.POST.get('is_active') or None

        profile_image = request.FILES.get('profile_image') or None
        face_embedding = None
        if profile_image:
            if verify_image(request, profile_image, 'user:edit_user', id) is not True:
                return verify_image(request, 'user:edit_user', id)

            face_embedding = get_face_embedding(profile_image)
            image_path = save_profile_image(profile_image, 'profile_image')
        else:
            image_path = user.profile_image

        user.username = username
        if password:
            user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.birthday = birthday
        user.gender = gender
        user.email = email
        user.phone = phone
        user.is_superuser = is_superuser
        user.is_staff = is_staff
        user.is_active = is_active
        user.profile_image = image_path

        user.save()
        if profile_image:
            delete_single_image(old_profile_image, 'profile_image')

            if face_embedding is not None:
                face_identity = FaceID.objects.filter(user_id=user.id).first()
                if face_identity:
                    face_identity.set_embedding(face_embedding)
                face_identity.save()

            if user.username != old_username:
                detect_result_list = Item.objects.filter(user=old_username).all()
                for detect_result in detect_result_list:
                    detect_result.user = user.get_full_name()
                    detect_result.save()

                detect_record_list = MonitoringRecord.objects.filter(user=old_username).all()
                for detect_record in detect_record_list:
                    detect_record.user = user.get_full_name()
                    detect_record.save()

        return hint_message(request, 'Edit successful!', 'user:user_list')


class UserInfo(LoginRequiredMixin, View):

    def get(self, request):

        user = request.user
        is_superuser = user.is_superuser
        if not user:
            return hint_message(request, 'User not found.', 'account:account')

        return render(request, 'user/register_add_edit_info_user.html',
                      { 'page': 'user_info', 'user': user})

    def post(self, request):

        id = request.user.id
        user = User.objects.filter(id=id).first()

        if not user:
            return hint_message(request, 'User not found.', 'account:account')

        old_username = user.username
        old_image = user.profile_image.name.split('/')[-1]

        username = request.POST.get('username') or None
        if verify_username(request, username, 'user:user_info') is not True:
            return verify_username(request, username, 'user:user_info')

        password = request.POST.get('password') or None

        confirm_password = request.POST.get('confirm_password') or None

        if password is not None and confirm_password is not None:
            if verify_password(request, password, 'user:add_user') is not True:
                return verify_password(request, password, 'user:user_info')

            if verify_password(request, confirm_password, 'user:add_user') is not True:
                return verify_password(request, confirm_password, 'user:usr_info')

        first_name = request.POST.get('first_name') or None
        last_name = request.POST.get('last_name') or None
        if verify_first_last_name(request, first_name, last_name, 'user:user_info') is not True:
            return verify_first_last_name(request, first_name, last_name, 'user:user_info')

        birthday = request.POST.get('birthday') or None
        gender = request.POST.get('gender') or None
        phone = request.POST.get('phone') or None

        if verify_phone(request, phone, 'user:user_info') is not True:
            return verify_phone(request, phone, 'user:user_info')

        if phone:
            if phone[0] != '6':
                phone = '6' + phone

        email = request.POST.get('email') or None

        if verify_email(request, email, 'user:user_info') is not True:
            return verify_email(request, email, 'user:user_info')

        if verify_user_exists(request, username, email, phone, 'user:user_info', id) is not True:
            return verify_user_exists(request, username, email, phone, 'user:user_info', id)

        is_superuser = request.POST.get('is_superuser') or user.is_superuser
        is_staff = request.POST.get('is_staff') or user.is_staff
        is_active = request.POST.get('is_active') or user.is_active

        profile_image = request.FILES.get('profile_image') or None
        face_embedding = None
        if profile_image:
            if verify_image(request, profile_image, 'user:user_info') is not True:
                return verify_image(request, profile_image, 'user:user_info')

            face_embedding = get_face_embedding(profile_image)

            image_path = save_profile_image(profile_image, 'profile_image')
        else:
            image_path = user.profile_image

        user.username = username

        if password:
            user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.birthday = birthday
        user.gender = gender
        user.email = email
        user.phone = phone
        user.is_superuser = is_superuser
        user.is_staff = is_staff
        user.is_active = is_active
        user.profile_image = image_path

        user.save()

        if profile_image:
            delete_single_image(old_image, 'profile_image')

            if face_embedding is not None:
                face_identity = FaceID.objects.filter(user_id=user.id).first()
                if face_identity:
                    face_identity.set_embedding(face_embedding)
                face_identity.save()

            if user.username != old_username:
                detect_result_list = Item.objects.filter(user=old_username).all()
                for detect_result in detect_result_list:
                    detect_result.user = user.get_full_name()
                    detect_result.save()

                detect_record_list = MonitoringRecord.objects.filter(user=old_username).all()
                for detect_record in detect_record_list:
                    detect_record.user = user.get_full_name()
                    detect_record.save()

        return hint_message(request, 'Update successful!', 'monitoring:get_monitoring_display_and_detect_data')
