# =============================================================================
# apps.py
# Author: Aidan Lelliott
# Organization: ASW
# Date: 10/08/2025
# Version: 1.0.0
#
# Description:
#   Django apps
# 
#
# License: Proprietary - For internal use only. Do not distribute.
# =============================================================================

from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
