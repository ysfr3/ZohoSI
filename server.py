import os
from waitress import serve
from zohosi.wsgi import application
if __name__ == '__main__':
   serve(application, port=f'{os.environ.get("X_ZOHO_CATALYST_LISTEN_PORT")}')