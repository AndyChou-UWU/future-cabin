import os
import sys

# 1. 取得當前根目錄的物理絕對路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 將所有層級資料夾一鍵灌入 Python 的最高搜尋核心
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'smart_cabin_project'))
sys.path.insert(0, os.path.join(BASE_DIR, 'smart_cabin_project', 'smart_cabin_project'))
sys.path.insert(0, os.path.join(BASE_DIR, 'smart_cabin_project', 'my_cabin'))

# 3. 【最核心修正！】：直接指向雙層資料夾內的設定檔
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_cabin_project.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
