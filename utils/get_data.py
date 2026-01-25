from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from user_agents import parse


def get_data_by_page(data, page):
    paginator = Paginator(data, 20)
    page = page
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)
    is_paginated = True if paginator.num_pages > 1 else False

    return [data, is_paginated]


def get_device_info(request):
    ua_string = request.META.get("HTTP_USER_AGENT", "")
    user_agent = parse(ua_string)

    return {
        "browser": f"{user_agent.browser.family} {user_agent.browser.version_string}",
        "system": f"{user_agent.os.family} {user_agent.os.version_string}",
        "device": user_agent.device.family,
        "is_mobile": user_agent.is_mobile,
        "is_tablet": user_agent.is_tablet,
        "is_pc": user_agent.is_pc,
        "is_bot": user_agent.is_bot,
    }