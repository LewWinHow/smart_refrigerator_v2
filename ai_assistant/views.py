from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from rest_framework.views import APIView

from ai_assistant.models import Chat, VoiceInteractionChat
from utils.audio_to_text import audio_to_text
from utils.llm import *


# Create your views here.
class GetChat(LoginRequiredMixin, APIView):
    def get(self, request):
        user = request.user
        is_superuser = user.is_superuser
        if Chat.objects.filter(user=user).exists() is False:
            message = Chat.objects.create(
                message="Hi, I'm your NEIVCE smart refrigerator assistant Xiao Xue. How can I help you?", user=user,
                sender=2)
            message.save()

        chat_list = Chat.objects.filter(user=user).all()
        message_precessing = False
        if Chat.objects.last().message == '⚫⚫⚫':
            message_precessing = True
        return render(request, 'ai_assistant/chat.html',
                      {'chat_list': chat_list, 'is_superuser': is_superuser, 'message_processing': message_precessing})

    def post(self, request):
        user = request.user
        message = (request.data.get('message', '') or '').strip() or None

        if message is None:
            return JsonResponse({'error': 'Empty message'}, status=400)

        # Save user message
        Chat.objects.create(message=message, user=user, sender=1)
        # Save processing AI response
        Chat.objects.create(message='⚫⚫⚫', user=user, sender=2)

        chat_list = Chat.objects.filter(user=user).all()
        data = {
            'chat_list': [
                {
                    'message': chat.message,
                    'sender': chat.sender
                } for chat in chat_list
            ]
        }
        return JsonResponse(data)


class ClearChat(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        chat_list = Chat.objects.filter(user=user).all()
        chat_list.delete()

        return redirect('ai_assistant:get_chat')


class ReceiveMessageAndUseLLM(LoginRequiredMixin, APIView):
    def post(self, request):

        user = request.user
        message = (request.data.get('message', '') or '').strip() or None
        if message is None:
            return redirect('ai_assistant:get_chat')

        chat_list = Chat.objects.filter(user=user).all()
        message_history = ''
        for chat_history in chat_list:
            if chat_history.sender == 1:
                message_history += f'''User input: {chat_history.message}\n'''
            elif chat_history.sender == 2:
                message_history += f'''You responded: {chat_history.message}\n'''

        title = response_title(message, message_history)

        response = ''
        if title == '1':
            print('1')
            response = response_with_title1(message, message_history, user)
        elif title == '2':
            print('2')
            response = response_with_title2(message, message_history)
        elif title == '3':
            print('3')
            response = response_with_title3(message, message_history, user)
        elif title == '4':
            print('4')
            response = response_with_title4(message, message_history)
        elif title == '5':
            print('5')
            response = response_with_title5(message, message_history)
        else:
            print('6')
            response = response_with_title6(message, message_history)

        old_chat_by_LLM_response = Chat.objects.filter(user=user, sender=2).last()
        old_chat_by_LLM_response.delete()
        new_chat_by_LLM_response = Chat.objects.create(message=response, user=user, sender=2)
        new_chat_by_LLM_response.save()

        chat_list = Chat.objects.filter(user=user).all()
        data = {
            'chat_list': [
                {
                    'message': chat.message,
                    'sender': chat.sender
                } for chat in chat_list
            ]
        }
        return JsonResponse(data)


class ReceiveAudioAndConvertToText(LoginRequiredMixin, APIView):
    def post(self, request):
        # Check if it's an audio request (optional)
        is_audio = request.POST.get('is_audio') == '1'

        # File is in request.FILES
        audio = request.FILES.get('audio') or None
        if not audio:
            return JsonResponse({'error': 'No audio file'}, status=400)

        text = audio_to_text(audio)
        print(text)
        data = {
            'text': text
        }
        return JsonResponse(data)


class ReceiveAudioAndResponse(APIView):
    def post(self, request):
        user = request.user
        # Check if it's an audio request (optional)
        is_audio = request.POST.get('is_audio') == '1'

        # File is in request.FILES
        audio = request.FILES.get('audio') or None
        if not audio:
            return JsonResponse({'error': 'No audio file'}, status=400)

        voice_interaction_list = VoiceInteractionChat.objects.all()
        message_history = ''
        for voice_interaction in voice_interaction_list:
            if voice_interaction.sender == 1:
                message_history += f'''User input: {voice_interaction.message}\n'''
            elif voice_interaction.sender == 2:
                message_history += f'''You responded: {voice_interaction.message}\n'''

        text = audio_to_text(audio)

        print(text)
        # if not 'Xiao Hao Classmate' in text and not 'Xiao Hao Classmate' in text:
        #     data = {
        #         'reply':None
        #     }
        #     return JsonResponse(data)

        title = response_title(text, message_history)
        print(title)

        response = ''
        if title == '1':
            print('1')
            response = response_with_title1(text, message_history, user)
        elif title == '2':
            print('2')
            response = response_with_title2(text, message_history)
        elif title == '3':
            print('3')
            response = response_with_title3(text, message_history, user)
        elif title == '4':
            print('4')
            response = response_with_title4(text, message_history)
        elif title == '5':
            print('5')
            response = response_with_title5(text, message_history)
        else:
            print('6')
            response = response_with_title6(text, message_history)

        VoiceInteractionChat.objects.create(message=text, sender=1).save()
        VoiceInteractionChat.objects.create(message=response, sender=2).save()

        data = {
            'reply': response,
        }
        return JsonResponse(data)
