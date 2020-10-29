from django.urls import path
from .views import Home, Software,ImportFile,ImportText, ProcessFiles, delete_file, soft_review, prev_review, next_review, del_review, update_review, del_software, export_file
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', Home, name='Home'),
    path('<int:pk>/', delete_file, name='delete_file'),
    path('importfile/', ImportFile , name='importfile'),
    path('importtext/', ImportText , name='importtext'),
    path('processfiles/', ProcessFiles , name='ProcessFiles'),
    path('review/', soft_review, name='ReviewSoft'),
    path('deletereview/<int:pk>/', del_review, name='delreview'),
    path('prevreview/<int:pk>/', prev_review, name='prevdoc'),
    path('nextreview/<int:pk>/', next_review, name='nextdoc'),
    path('updatereview/<int:pk>/', update_review, name='update_review'),
    path('software/',Software, name='Software'),
    path('deletesoftware/<int:pk>/', del_software, name='del_software'),
    path('export/', export_file, name='export_file')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)