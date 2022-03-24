from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from wayrem_admin.AlterModelsScript import AlterModelsCreate

urlpatterns = [
    path('', include('wayrem_admin.urls', namespace='wayrem_admin')),
    # path('', include("wayrem_admin.urls")),
    path('admin/', admin.site.urls),
    path('Altermodelscreate/<str:key>', AlterModelsCreate, name="AlterModelsCreate"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
