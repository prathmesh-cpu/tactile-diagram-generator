from django.contrib import admin
from django.urls import path
from home import views
from home.views import process_image
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name = "home"),
    path('index/', views.index, name = "index"),
    path('textBraille/', views.text, name = "textBraille"),
    path('upload/', process_image, name='upload'),
    # path('', process_image, name='upload')
    # path('', views.text, name='textBraille')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)