from django.urls import path
from .views import Home, Software,ImportFile,ImportText, ProcessFiles, delete_file, soft_review, prev_review, next_review, del_review, submit_review, del_software, export_file, change_soft, submit_soft, pushsuccess
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
    path('submitreview/<int:pk>/', submit_review, name='submit_review'),
    path('software/',Software, name='Software'),
    path('deletesoftware/<int:pk>/', del_software, name='del_software'),
    path('changesoft/<int:pk>/',change_soft, name='change_soft'),
    path('submitsoft/<int:pk>/',submit_soft, name='submit_soft'),
    path('export/', export_file, name='export_file'),
    path('pushsuccess/', pushsuccess, name='pushsuccess')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)