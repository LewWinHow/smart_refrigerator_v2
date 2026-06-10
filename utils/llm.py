import json
import os
import django

import user

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_refrigerator_v2.settings')
django.setup()
import requests

from item.models import Item
from utils.rag import search_recipe, search_ingredient_storage_method


def llm(prompt, model='gpt-oss:120b-cloud'):
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': model,
            'prompt': prompt
        },
        stream=True
    )

    result = ''

    for line in response.iter_lines():
        if not line:
            continue

        try:
            data = json.loads(line.decode('utf-8'))
            if 'response' in data:
                result += data['response']
        except json.JSONDecodeError:
            continue

    return result.strip()


def response_language(message):
    prompt = f'''Return the language name based on user input.\n\n

                User input: {message}
'''
    return llm(prompt)


def response_title(message, message_history):
    prompt = f'''You are a shared smart refrigerator assistant named Xiao Xue. Based on the user input and previous chat history, determine the current topic and return one of the following numbers:\n
                    1. Get ingredients in the refrigerator.
                    2. Recipes and cooking methods, if the user did not specify using existing ingredients in the refrigerator, choose this.\n
                    3. Recipes and cooking methods, if the user specified using existing ingredients in the refrigerator, choose this.\n
                    4. Ingredient storage methods.\n
                    5. Other topics related to refrigerators, ingredients, or recipes.\n
                    6. Topics unrelated to refrigerators, ingredients, or recipes.\n\n

                    Previous chat history:\n
                    {message_history}\n\n

                    User input: {message}
    '''
    return llm(prompt)


def response_with_title1(message, message_history, user):
    item_list = []
    user_item_list = []

    for item in Item.objects.all():
        item_list.append(item.item)

    for item in Item.objects.filter(user=user).all():
        user_item_list.append(item.item)

    prompt = f'''You are a shared smart refrigerator assistant named Xiao Xue. The user wants to get the current ingredients in the refrigerator. You need to answer separately for all ingredients in the refrigerator and the ingredients placed by the user. Answer directly in plain language, focusing on key points without special symbols. If the user asks in Chinese, answer in Chinese; if the user asks in English, answer in English.\n\n

                All ingredients in the refrigerator: {item_list if item_list else 'None'}.\n\n

                Ingredients placed by this user: {user_item_list if item_list else 'None'}.\n\n

                Previous chat history:\n
                {message_history}\n\n

                User input: {message}
            '''
    return llm(prompt)


def response_with_title2(message, message_history):
    ingredient_and_recipe = extract_ingredient_and_recipe(message)
    search_result = search_recipe(ingredient_and_recipe)
    prompt = f'''You are a shared smart refrigerator assistant named Xiao Xue. You need to recommend recipes and cooking methods to the user. There is no need to base recommendations on existing ingredients in the refrigerator. Shorten sentences and focus on key points. Do not use tables; answer directly in plain language without special symbols. If the user asks in Chinese, answer in Chinese; if the user asks in English, answer in English.\n\n

                Recipes and cooking methods found using the search engine for ingredients and recipes {search_result}:\n
                {search_result}\n\n\

                Please integrate the recipes and cooking methods found above.\n\n

                Previous chat history:\n
                {message_history}\n\n

                User input: {message}
            '''

    return llm(prompt)


def extract_ingredient_and_recipe(message):
    prompt = f'''Return the ingredients and recipes mentioned in the user input. The return format must be like "tomato egg salted chicken". If the ingredients or recipes are in English, translate them into Chinese and return.\n\n

                User input: {message}
                '''

    return llm(prompt)



def response_with_title3(message, message_history, user):
    item_list = []
    user_item_list = []

    for item in Item.objects.all():
        item_list.append(item.item)

    for item in Item.objects.filter(user=user).all():
        user_item_list.append(item.item)

    recipes_with_item_list = search_recipe(item_list)
    recipes_with_user_item_list = search_recipe(user_item_list)

    prompt = f'''You are a shared smart refrigerator assistant named Xiao Xue. You need to recommend recipes and cooking methods to the user based on all existing ingredients in the refrigerator and the ingredients placed by the user separately.
    If there are no ingredients in the refrigerator or the user has not placed any ingredients, reply directly that there are no ingredients in the refrigerator or the user has not placed any ingredients. Shorten sentences and focus on key points. Do not use tables; answer directly in plain language without special symbols.
    If the user asks in Chinese, answer in Chinese; if the user asks in English, answer in English.\n\n

                All ingredients in the refrigerator: {item_list if item_list else 'None'}\n\n

                Ingredients placed by this user: {user_item_list if user_item_list else 'None'}\n\n

                Recipes and cooking methods found using the search engine for ingredients and recipes {recipes_with_item_list} available in the refrigerator:\n
                {recipes_with_item_list}\n\n

                Recipes and cooking methods found using the search engine for ingredients and recipes {recipes_with_item_list} placed by the user in the refrigerator:\n
                {recipes_with_user_item_list}\n\n

                Please integrate the recipes and cooking methods found above.\n\n

                Previous chat history:\n
                {message_history}\n\n

                User input: {message}
            '''
    return llm(prompt)


def response_with_title4(message, message_history):
    ingredient_and_recipe = extract_ingredient_and_recipe(message)
    search_result = search_ingredient_storage_method(ingredient_and_recipe)

    prompt = f'''You are a shared smart refrigerator assistant named Xiao Xue. You need to recommend ingredient storage methods to the user. Shorten sentences and focus on key points. Do not use tables; answer directly in plain language without special symbols. If the user asks in Chinese, answer in Chinese; if the user asks in English, answer in English.\n\n
    
                Ingredient storage methods found using the search engine for ingredients {ingredient_and_recipe}:\n
                {search_result}\n\n
                
                Please integrate the ingredient storage methods found above.\n\n

                Previous chat history:\n
                {message_history}\n\n

                User input: {message}
            '''

    return llm(prompt)


def response_with_title5(message, message_history):
    prompt = f'''You are a shared smart refrigerator assistant named Xiao Xue. The user wants to ask questions about refrigerators, ingredients, and recipes. Shorten sentences and focus on key points. Do not use tables; answer directly in plain language without special symbols. If the user asks in Chinese, answer in Chinese; if the user asks in English, answer in English.\n\n

                Previous chat history:\n
                {message_history}\n\n

                User input: {message}
            '''

    return llm(prompt)


def response_with_title6(message, message_history):
    prompt = f'''You are a shared smart refrigerator assistant named Xiao Xue. The user wants to ask questions unrelated to refrigerators, ingredients, and recipes. Shorten sentences and focus on key points. Do not use tables; just give a simple answer to the user. Answer directly in plain language without special symbols. If the user asks in Chinese, answer in Chinese; if the user asks in English, answer in English.\n\n

                Previous chat history:\n
                {message_history}\n\n

                User input: {message}
            '''

    return llm(prompt)
