def resolve_image(value, fallback):
    if not value:
        return fallback
        
    # Convert to string and check for URLs first
    raw_value = str(value)
    if raw_value.startswith('http'):
        return raw_value
        
    # Handle ImageField objects (from admin uploads)
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