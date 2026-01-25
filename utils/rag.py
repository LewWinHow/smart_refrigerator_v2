from ddgs import DDGS


def search_recipe(ingredients, max_results=5):
    query = f'{" ".join(ingredients)} 家常菜 做法 怎么做'

    recipes = []
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            for r in results:
                recipes.append({
                    'title': r.get('title', ''),
                    'url': r.get('href', ''),
                    'summary': r.get('body', '')
                })
    except Exception as e:
        print(f'Search error: {e}')

    return recipes


def search_ingredient_storage_method(ingredients, language='中文', max_results=5):
    query = f'{" ".join(ingredients)} 保存方法 储存 冰箱 保鲜'

    recipes = []
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            for r in results:
                recipes.append({
                    'title': r.get('title', ''),
                    'url': r.get('href', ''),
                    'summary': r.get('body', '')
                })
    except Exception as e:
        print(f'Search error: {e}')

    return recipes
