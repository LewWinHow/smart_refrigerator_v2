from django.urls import path
from account import views
from account.views import *

app_name = 'account'

urlpatterns = [
    # Login related
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('forgot_password/', ForgotPassword.as_view(), name='forgot_password'),
    path('verification_code/', VerificationCode.as_view(), name='verification_code'),
    path('reset_password/', ResetPassword.as_view(), name='reset_password'),
    path('register/', Register.as_view(), name='register'),
    path('get_captcha/', GetCaptcha.as_view(), name='get_captcha'),
]
