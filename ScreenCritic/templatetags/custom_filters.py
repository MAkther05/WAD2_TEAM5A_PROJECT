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
def route_name_review(media_type):
    if media_type == "TV Show":
        return 'ScreenCritic:tv_review'
    elif media_type == "Movie":
        return 'ScreenCritic:movie_review'
    elif media_type == "Game":
        return 'ScreenCritic:game_review'
    return 'ScreenCritic:home'