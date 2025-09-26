from django.urls import path
from .views import PushSendToSI, PullSendToSI, PushSendToCRM

urlpatterns = [
    path('si/', PushSendToSI.as_view(), name='push-sendtosi'),
    path('si/<int:pk>', PullSendToSI.as_view(), name='pull-sendtosi'),
    path('crm/', PushSendToCRM.as_view(), name='push-sendtocrm'),
]