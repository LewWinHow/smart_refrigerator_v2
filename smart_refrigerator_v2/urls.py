from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('account/', include('account.urls')),
                  path('login_log/', include('login_log.urls')),
                  path('monitoring/', include('monitoring.urls')),
                  path('temperature_and_humidity/', include('temperature_and_humidity.urls')),
                  path('', RedirectView.as_view(url='/account/login/', permanent=False)),
                  path('user/', include('user.urls')),
                  path('item/', include('item.urls')),
                  path('ai_assistant/', include('ai_assistant.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
