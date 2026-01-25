import os.path

from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views import View

from item.models import Item
from utils.draw_and_save_image import draw_and_save_image
from utils.delete_image import delete_single_image
from rest_framework.views import APIView
from utils.delete_image import delete_all_images
from utils.detect_item import *
from utils.verify import *
from monitoring.models import *
from utils.detect_face import *
from utils.send_email_for_warning import send_email_for_warning


class ReceiveAndDetectImage(APIView):
    def post(self, request):
        connect = request.POST.get('connect') or None
        if connect == '0':
            MonitoringDisplay.objects.all().delete()
            delete_all_images('monitoring_display')
            return HttpResponse('Disconnect.')
        detect_frame_list = MonitoringDisplay.objects.all()
        if detect_frame_list.count() > 10:
            for detect_display in detect_frame_list[:10]:
                frame_image = detect_display.image.name.split('/')[-1]
                delete_single_image(frame_image, 'monitoring_display')
                detect_display.delete()

        image = request.FILES['image']
        if not image:
            return HttpResponse('No image provided')
        if image.content_type != 'image/jpeg':
            return HttpResponse('Not JPEG image')

        face_name, face_box = detect_face(image)
        item_label, item_box = detect_item(image)
        now_detect_time = datetime.now()

        if face_name:

            if item_label:
                item = Item.objects.filter(item=item_label).first()
                detect_record_by_item = MonitoringRecord.objects.filter(item=item_label).last()

                if item and detect_record_by_item:
                    time_equation = now_detect_time - detect_record_by_item.record_time

                    if detect_record_by_item.action == 1:
                        item_image = item.image.name.split('/')[-1]
                        delete_single_image(item_image, 'item')

                        if time_equation.seconds > 5:
                            folders = ['monitoring_display', 'monitoring_record']
                            item.delete()
                            image_paths = draw_and_save_image(image, face_name, face_box, item_label, item_box,
                                                              folders)

                            detect_record = MonitoringRecord(item=item_label, action=0,
                                                             image=image_paths['monitoring_record'],
                                                             user=face_name,
                                                             record_time=now_detect_time)
                            detect_display = MonitoringDisplay(image=image_paths['monitoring_display'])
                            detect_record.save()
                            detect_display.save()

                            if face_name != item.user and item.user != 'unknown' and item.permissions != 1:
                                user = User.objects.filter(username=item.user).first()
                                email = user.email
                                image_path = os.path.join(settings.MEDIA_ROOT, image_paths['monitoring_record'])
                                send_email_for_warning(email, image_path)

                            return HttpResponse(
                                f"Detect Face: {'Yes(' + face_name + ')' if face_name else 'No'}, Detect Item: Detect take out item({item_label})")
                        else:
                            folders = ['item', 'monitoring_record', 'monitoring_display']
                            image_paths = draw_and_save_image(image, face_name, face_box, item_label, item_box,
                                                              folders)
                            item.image = image_paths['item']
                            item.record_time = now_detect_time
                            item.user = face_name
                            detect_record = MonitoringRecord(item=item_label, action=1,
                                                             image=image_paths['monitoring_record'],
                                                             user=face_name,
                                                             record_time=now_detect_time)
                            detect_display = MonitoringDisplay(image=image_paths['monitoring_display'])
                            item.save()
                            detect_record.save()
                            detect_display.save()
                            return HttpResponse(
                                f"Detect Face: {'Yes(' + face_name + ')' if face_name else 'No'}, Detect Item: Detect putting in item({item_label})")
                elif not item and detect_record_by_item:
                    time_equation = now_detect_time - detect_record_by_item.record_time

                    if time_equation.seconds > 5:
                        folders = ['item', 'monitoring_record', 'monitoring_display']
                        image_paths = draw_and_save_image(image, face_name, face_box, item_label, item_box,
                                                          folders)
                        item = Item(item=item_label, image=image_paths['item'],
                                    user=face_name,
                                    permissions=0,
                                    record_time=now_detect_time)
                        detect_record = MonitoringRecord(item=item_label,
                                                         image=image_paths['monitoring_record'],
                                                         action=1, user=face_name,
                                                         record_time=now_detect_time)
                        detect_display = MonitoringDisplay(image=image_paths['monitoring_display'])
                        item.save()

                        detect_record.save()
                        detect_display.save()
                        return HttpResponse(
                            f"Detect Face: {'Yes(' + face_name + ')' if face_name else 'No'}, Detect Item: Detect new item({item_label})")
                    else:
                        folders = ['monitoring_record', 'monitoring_display']
                        image_paths = draw_and_save_image(image, face_name, face_box, item_label, item_box,
                                                          folders)
                        detect_record = MonitoringRecord(item=item_label, action=0,
                                                         image=image_paths['monitoring_record'],
                                                         user=face_name,
                                                         record_time=now_detect_time)
                        detect_display = MonitoringDisplay(image=image_paths['monitoring_display'])
                        detect_record.save()
                        detect_display.save()
                        return HttpResponse(
                            f"Detect Face: {'Yes(' + face_name + ')' if face_name else 'No'}, Detect Item: Detect taking out item({item_label})")
                else:
                    folders = ['item', 'monitoring_record', 'monitoring_display']
                    image_paths = draw_and_save_image(image, face_name, face_box, item_label, item_box, folders)
                    item = Item(item=item_label, image=image_paths['item'],
                                user=face_name,
                                permissions=0,
                                record_time=now_detect_time)
                    detect_record = MonitoringRecord(item=item_label, image=image_paths['monitoring_record'], action=1,
                                                     user=face_name,
                                                     record_time=now_detect_time)
                    detect_display = MonitoringDisplay(image=image_paths['monitoring_display'])
                    item.save()
                    detect_display.save()
                    detect_record.save()
                    return HttpResponse(
                        f"Detect Face: {'Yes(' + face_name + ')' if face_name else 'No'}, Detect Item: Detect new item({item_label})")
            else:
                folders = ['monitoring_display']
                image_paths = draw_and_save_image(image, face_name, face_box, None, None, folders)
                detect_display = MonitoringDisplay(image=image_paths['monitoring_display'])
                detect_display.save()
                return HttpResponse(f"Detect Face: {'Yes(' + face_name + ')' if face_name else 'No'}, Detect Item: No")
        else:
            folders = ['monitoring_display']
            image_paths = draw_and_save_image(image, None, None, None, None, folders)
            detect_display = MonitoringDisplay(image=image_paths['monitoring_display'])
            detect_display.save()
            return HttpResponse(f'Detect Face: No, Detect Item: No')


class SetItemPermissions(LoginRequiredMixin, View):
    def get(self, request, item_id):

        user = request.user
        if verify_superuser(user) is not True:
            return verify_superuser(user)

        item = Item.objects.filter(id=item_id, user=user.username).last()
        if item is None:
            return hint_message(request, 'Item not found.', 'monitoring:monitoring:get_monitoring_display_and_detect_data')

        if item.permissions == 0:
            item.permissions = 1
        else:
            item.permissions = 0

        item.save()
        return redirect('monitoring:get_monitoring_display_and_detect_data')
