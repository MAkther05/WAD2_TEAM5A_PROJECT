from django import template

register = template.Library()

@register.filter
def route_name(media_type):
    """Return the correct URL route name based on media type"""
    if media_type == 'TV Show':
        return 'ScreenCritic:tv_detail'
    elif media_type == 'Movie':
        return 'ScreenCritic:movie_detail'
    elif media_type == 'Game':
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

@register.filter
def resolve_image(value, fallback='/static/images/logo.png'):
    """Resolve image URL from either ImageField or direct URL"""
    if not value:
        return fallback
        
    # Handle direct URLs
    raw_value = str(value)
    if raw_value.startswith('http'):
        return raw_value
        
    # Handle ImageField objects
    if hasattr(value, 'url'):
        try:
            url = value.url
            # If the URL was stored as a full URL, extract it from the media path
            if 'https%3A' in url:
                return url.split('/media/')[-1].replace('%3A', ':')
            return url
        except ValueError:
            pass
            
    return fallback