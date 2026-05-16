import os
import sys
from django.core.wsgi import get_wsgi_application

# 這樣不論它在內層還是外層，都能百分之百動態抓到 settings 檔案！
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_cabin_project.smart_cabin_project.settings')

application = get_wsgi_application()
