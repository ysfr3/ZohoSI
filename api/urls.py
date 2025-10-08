# =============================================================================
# urls.py
# Author: Aidan Lelliott
# Organization: ASW
# Date: 10/08/2025
# Version: 1.0.0
#
# Description:
#   URL routing for Zoho SI API endpoints.
#
# License: Proprietary - For internal use only. Do not distribute.
# =============================================================================

from django.urls import path
from .views import PushSendToSI, PullSendToSI, PushSendToCRM

urlpatterns = [
    path('si/', PushSendToSI.as_view(), name='push-sendtosi'),
    path('si/<int:pk>', PullSendToSI.as_view(), name='pull-sendtosi'),
    path('crm/', PushSendToCRM.as_view(), name='push-sendtocrm'),
]