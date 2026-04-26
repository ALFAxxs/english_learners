from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('game.urls')),
    re_path(r'^static/(?P<path>.*)$',  serve, {'document_root': settings.STATICFILES_DIRS[0]}),
    re_path(r'^media/(?P<path>.*)$',   serve, {'document_root': settings.MEDIA_ROOT}),
]

handler400 = 'game.views.error_400'
handler403 = 'game.views.error_403'
handler404 = 'game.views.error_404'
handler500 = 'game.views.error_500'