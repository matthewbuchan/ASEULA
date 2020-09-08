from django.urls import path
from .views import Home, Software,ImportFile,ImportText, ReviewSoft, ProcessFiles, delete_file, ReviewSoftPrev, ReviewSoftNext
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', Home, name='Home'),
    path('<int:pk>/', delete_file, name='delete_file'),
    path('importfile/', ImportFile , name='importfile'),
    path('importtext/', ImportText , name='importtext'),
    path('processfiles/', ProcessFiles , name='ProcessFiles'),
    path('review/', ReviewSoft, name='ReviewSoft'),
    path('reviewprev/<int:pk>/', ReviewSoftPrev, name='reviewprev'),
    path('reviewnext/<int:pk>/', ReviewSoftNext, name='reviewnext'),
    path('software/',Software, name='Software'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)