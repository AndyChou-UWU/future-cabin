import os
import sys

# 1. 取得當前根目錄的物理絕對路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 強制將外層、內層、雙胞胎層所有資料夾一鍵灌入 Python 的最高搜尋核心
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'smart_cabin_project'))
sys.path.insert(0, os.path.join(BASE_DIR, 'smart_cabin_project', 'smart_cabin_project'))
sys.path.insert(0, os.path.join(BASE_DIR, 'smart_cabin_project', 'my_cabin'))

# 3. 強制指定 settings 的搜尋路徑（不管它認哪一個，通通能被 sys.path 抓到）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
