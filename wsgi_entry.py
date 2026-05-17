import os
import sys

# 1. 取得當前根目錄的物理絕對路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 將所有層級資料夾一鍵灌入 Python 的最高搜尋核心
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'smart_cabin_project'))

# 3. 【最核心修正！】：直接指向雙層資料夾內的設定檔
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_cabin.settings')

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

application = get_wsgi_application()
application = WhiteNoise(application, root=os.path.join(BASE_DIR, 'staticfiles'))
