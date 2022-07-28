from django.conf import settings  # import the settings file
from wayrem import constant


def admin_media(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'DOCUMENT_URL': constant.DOCUMENT_URL}
