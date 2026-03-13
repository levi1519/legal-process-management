from django.conf import settings

def get_image(image):
    """
    Return a URL for the given image, using storage-aware URLs when possible.

    If `image` is a Django File/ImageField (or similar) with a `.url` attribute,
    use that. Otherwise, if `image` is truthy (e.g. a relative path string),
    fall back to prefixing it with `MEDIA_URL`. If `image` is empty or None,
    return the default image path.
    """
    if image:
        # Use storage-aware URL when available (handles remote storages like S3).
        if hasattr(image, "url"):
            return image.url
        # Fallback for cases where `image` is a plain relative path string.
        return "{}{}".format(settings.MEDIA_URL, image)
    return "/static/img/default.jpg"  # default image