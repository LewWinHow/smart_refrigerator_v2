from ddgs import DDGS


def search_recipe(ingredients, max_results=5):
    query = f'{" ".join(ingredients)} home cooking recipe how to make'

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


def search_ingredient_storage_method(ingredients, language='English', max_results=5):
    query = f'{" ".join(ingredients)} storage method preservation refrigerator fresh keeping'

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
