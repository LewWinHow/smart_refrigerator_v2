from django.urls import path

from item.views import ReceiveAndDetectImage, SetItemPermissions

app_name = 'item'

urlpatterns = [
    path('receive_and_detect_image/', ReceiveAndDetectImage.as_view(), name='receive_and_detect_image'),
    path('set_item_permissions/<int:item_id>', SetItemPermissions.as_view(),
         name='set_item_permissions'),
]
