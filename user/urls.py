from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('user_list/', views.UserList.as_view(), name='user_list'),
    path('user_list/<int:page>', views.UserList.as_view(), name='user_list'),
    path('add_user/', views.AddUser.as_view(), name='add_user'),
    path('edit_user/<int:id>/', views.EditUser.as_view(), name='edit_user'),
    path('delete_user/<int:id>/', views.DeleteUser.as_view(), name='delete_user'),
    path('user_status/<int:id>/', views.SetUserStatus.as_view(), name='user_status'),
    path( 'user_info/', views.UserInfo.as_view(), name='user_info'),
]