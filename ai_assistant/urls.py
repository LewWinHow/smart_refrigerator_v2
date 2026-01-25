from django.urls import path
from win32gui import GetTextCharacterExtra

from ai_assistant.views import *

app_name = 'ai_assistant'

urlpatterns = [
    path('get_chat/', GetChat().as_view(), name='get_chat'),
    path('clear_chat/', ClearChat.as_view(), name='clear_chat'),
    path('receive_message_and_use_LLM/', ReceiveMessageAndUseLLM.as_view(), name='receive_message_and_use_LLM'),
    path('receive_audio_and_convert_to_text/', ReceiveAudioAndConvertToText.as_view(), name='receive_audio_and_convert_to_text'),
    path('receive_audio_and_response/', ReceiveAudioAndResponse.as_view(),
         name='receive_audio_and_convert_to_text'),
]
