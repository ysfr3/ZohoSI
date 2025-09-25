from django.urls import path
from .views import PushSendToSI, PullSendToSI

urlpatterns = [
    path('si/', PushSendToSI.as_view(), name='push-sendtosi'),
    path('si/<int:pk>', PullSendToSI.as_view(), name='pull-sendtosi'),
]