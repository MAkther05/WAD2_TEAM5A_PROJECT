from django import template

register = template.Library()

@register.filter
def route_name(media_type):
    if media_type == "TV Show":
        return 'ScreenCritic:tv_detail'
    elif media_type == "Movie":
        return 'ScreenCritic:movie_detail'
    elif media_type == "Game":
        return 'ScreenCritic:game_detail'
    return 'ScreenCritic:home'

@register.filter
def general_route_name(media_type):
    if media_type == "TV Show":
        return 'ScreenCritic:tv_list'
    elif media_type == "Movie":
        return 'ScreenCritic:movie_list'
    elif media_type == "Game":
        return 'ScreenCritic:game_list'
    return 'ScreenCritic:home'