import os
import sys
from django.core.wsgi import get_wsgi_application

# 終極大絕：強迫 Python 把所有資料夾層級全部加入搜尋路徑
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'smart_cabin_project'))

# 這樣不論它在內層還是外層，都能百分之百動態抓到 settings 檔案！
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

application = get_wsgi_application()
