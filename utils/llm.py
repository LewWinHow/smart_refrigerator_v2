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
    prompt = f'''根据用户输入返回语言名。\n\n

                用户输入：{message}
'''
    return llm(prompt)


def response_title(message, message_history):
    prompt = f'''你是一个共享的智能冰箱助手小雪（Xiao Xue），根据用户输入和之前的聊天记录判断当前的话题并返回以下数字：\n
                    1. 获取冰箱里的食材。
                    2. 食谱与做法，如果用户没有说需要根据冰箱现有食材推荐就选这个里。\n
                    3. 食谱与做法，如果用户有说需要根据冰箱现有食材推荐就选这里。\n
                    4. 食材的保存方法。\n
                    5. 其他有关冰箱，食材，食谱的话题。\n
                    6. 和冰箱，食材，食谱没有关联的话题。\n\n

                    之前的聊天记录：\n
                    {message_history}\n\n

                    用户输入：{message}
    '''
    return llm(prompt)


def response_with_title1(message, message_history, user):
    item_list = []
    user_item_list = []

    for item in Item.objects.all():
        item_list.append(item.item)

    for item in Item.objects.filter(user=user).all():
        user_item_list.append(item.item)

    prompt = f'''你是一个共享的智能冰箱助手小雪（Xiao Xue），用户想要获取冰箱现有的食材，需要分别回答冰箱里所有的食材和用户放入的食材，直接用白话文重点回答不要有特殊符号。需要根据用户输入的语言来回答。\n\n

                冰箱里所有的食材：{item_list if item_list else '无'}。\n\n

                该用户在冰箱放入的食材：{user_item_list if item_list else '无'}。\n\n

                之前的聊天记录：\n
                {message_history}\n\n

                用户输入：{message}
            '''
    return llm(prompt)


def response_with_title2(message, message_history):
    ingredient_and_recipe = extract_ingredient_and_recipe(message)
    search_result = search_recipe(ingredient_and_recipe)
    prompt = f'''你是一个共享的智能冰箱助手小雪（Xiao Xue），你需要推荐食谱与做法给用户，无需根据冰箱现有食材推荐，把句子缩短直接说重点，不要使用表格的形式回答，直接用白话文重点回答不要有特殊符号。需要根据用户输入的语言来回答。\n\n

                使用搜索引擎根据{search_result}的食材和食谱搜索到的食谱与做法：\n
                {search_result}\n\n\

                请把以上搜索到的食谱与做法进行整合。\n\n

                之前的聊天记录：\n
                {message_history}\n\n

                用户输入：{message}
            '''

    return llm(prompt)


def extract_ingredient_and_recipe(message):
    prompt = f'''根据用户输入返回用户输入里面提到的食材和食谱，返回格式必须是“番茄 鸡蛋 盐酥鸡”一样的返回格式。如果食材或食谱是英文名需要翻译成中文并返回。\n\n

                用户输入：{message}
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

    prompt = f'''你是一个共享的智能冰箱助手小雪（Xiao Xue），你需要推荐食谱与做法给用户，需要根据冰箱所有现有食材和该用户在冰箱放入的食材分别推荐，
    如果冰箱没有食材或者冰箱有食材但是该用户没有放入任何食材在冰箱侧直接回复冰箱现在没有任何食材或用户没有放入任何食材，把句子缩短直接说重点，不要使用表格的形式回答，直接用白话文重点回答不要有特殊符号。
    需要根据用户输入的语言来回答。\n\n

                冰箱里所有的食材：{item_list if item_list else '无'}\n\n

                该用户在冰箱放入的食材：{user_item_list if user_item_list else '无'}\n\n

                使用搜索引擎根据冰箱里面有的{recipes_with_item_list}的食材和食谱搜索到的食谱与做法：\n
                {recipes_with_item_list}\n\n

                使用搜索引擎根据用户在冰箱放入的{recipes_with_item_list}的食材和食谱搜索到的食谱与做法：\n
                {recipes_with_user_item_list}\n\n

                请把以上搜索到的食谱与做法进行整合。\n\n

                之前的聊天记录：\n
                {message_history}\n\n

                用户输入：{message}
            '''
    return llm(prompt)


def response_with_title4(message, message_history):
    ingredient_and_recipe = extract_ingredient_and_recipe(message)
    search_result = search_ingredient_storage_method(ingredient_and_recipe)

    prompt = f'''你是一个共享的智能冰箱助手小雪（Xiao Xue），你需要推荐食材的保存方法给用户，把句子缩短直接说重点，不要使用表格的形式回答，直接用白话文重点回答不要有特殊符号。需要根据用户输入的语言来回答。\n\n
    
                使用搜索引擎根据{ingredient_and_recipe}的食材搜索到的食材保存方法：\n
                {search_result}\n\n
                
                请把以上搜索到的食材保存方法进行整合。\n\n

                之前的聊天记录：\n
                {message_history}\n\n

                用户输入：{message}
            '''

    return llm(prompt)


def response_with_title5(message, message_history):
    prompt = f'''你是一个共享的智能冰箱助手小雪（Xiao Xue），用户想要询问关于冰箱，食材和食谱的问题，把句子缩短直接说重点，不要使用表格的形式回答，直接用白话文重点回答不要有特殊符号。需要根据用户输入的语言来回答。\n\n

                之前的聊天记录：\n
                {message_history}\n\n

                用户输入：{message}
            '''

    return llm(prompt)


def response_with_title6(message, message_history):
    prompt = f'''你是一个共享的智能冰箱助手小雪（Xiao Xue），用户想要询问和冰箱，食材和食谱没有关联的问题，把句子缩短直接说重点，不要使用表格的形式回答，只需简单回答用户就好，直接用白话文重点回答不要有特殊符号。需要根据用户输入的语言来回答。\n\n

                之前的聊天记录：\n
                {message_history}\n\n

                用户输入：{message}
            '''

    return llm(prompt)
