# Railway 部署靜態資源 - Windows 環境修復指南

## 已完成的修復

### ✅ 1. manage.py 配置修正
**修改內容：**
```python
# 之前（錯誤）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_cabin_project.smart_cabin_project.settings')

# 之後（正確）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_cabin.settings')
```

### ✅ 2. Procfile 配置修正（用於 Railway）
```
release: python smart_cabin_project/manage.py collectstatic --noinput
web: gunicorn -w 4 -b 0.0.0.0:$PORT smart_cabin_project.my_cabin.wsgi
```

### ✅ 3. 相關 WSGI 檔案修正
- `wsgi_entry.py`
- `smart_cabin_project/my_cabin/wsgi.py`
- `smart_cabin_project/my_cabin/settings.py`

---

## 本地測試步驟（Windows）

### 在開發環境中測試
```powershell
# 1. 進入項目根目錄
cd "C:\Users\User\Downloads\python 學習檔案\smart_cabin_project"

# 2. 激活虛擬環境
.\venv\Scripts\Activate.ps1

# 3. 運行開發服務器（不需要 collectstatic）
python smart_cabin_project/manage.py runserver
```

**訪問：** http://127.0.0.1:8000/

✅ 如果看到頁面樣式正確顯示，靜態資源加載成功

---

## 模擬 Railway 生產環境（可選）

### 安裝 Windows 相容的 WSGI 服務器
```powershell
# 使用 waitress 代替 gunicorn（Windows 不支持 gunicorn）
pip install waitress
```

### 運行 collectstatic
```powershell
python smart_cabin_project/manage.py collectstatic --clear --noinput
```

### 使用 waitress 啟動
```powershell
waitress-serve --port=8000 smart_cabin_project.my_cabin.wsgi:application
```

---

## 部署到 Railway

### 1. 驗證所有修復檔案已保存
- [x] Procfile
- [x] smart_cabin_project/manage.py
- [x] smart_cabin_project/my_cabin/wsgi.py
- [x] wsgi_entry.py
- [x] smart_cabin_project/my_cabin/settings.py

### 2. 提交代碼
```bash
git add .
git commit -m "Fix static files configuration for Railway deployment"
git push
```

### 3. Railway 自動執行
Railway 會自動執行 Procfile 中的命令：
1. **release 階段** → 執行 `collectstatic` 收集靜態文件
2. **web 階段** → 啟動 gunicorn 服務

---

## 驗證清單

### 本地測試
- [ ] `python smart_cabin_project/manage.py runserver` 成功啟動
- [ ] 訪問 http://127.0.0.1:8000 看到完整樣式
- [ ] 瀏覽器開發工具 (F12) → Network 標籤，CSS/JS 狀態碼為 200

### Railway 部署後
- [ ] 部署完成（檢查 Railway Dashboard）
- [ ] 訪問應用 URL，看到完整樣式
- [ ] 查看 Railway Logs，確認 `collectstatic` 成功執行
- [ ] 開發工具驗證靜態資源狀態碼為 200

---

## 常見問題排查

### 問題 1：本地仍顯示 404
**解決：**
```powershell
# 清除快取
python smart_cabin_project/manage.py collectstatic --clear --noinput

# 重新啟動開發服務器
python smart_cabin_project/manage.py runserver
```

### 問題 2：Railway 部署後靜態資源仍為 404
**檢查步驟：**
1. Railway Dashboard → Deployment → Logs，查看 collectstatic 是否執行
2. 確認 `staticfiles/` 目錄包含文件
3. 檢查 settings.py 中的 `STATIC_ROOT` 是否正確：
   ```python
   STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
   ```

### 問題 3：Railway 部署超時
**解決：**
- 檢查虛擬環境中是否安裝了所有依賴
- 確認 `requirements.txt` 包含 `whitenoise`、`gunicorn` 等

---

## 關鍵配置檢查表

| 項目 | 位置 | 應該是 |
|------|------|--------|
| DJANGO_SETTINGS_MODULE | manage.py | `my_cabin.settings` |
| DJANGO_SETTINGS_MODULE | wsgi.py | `my_cabin.settings` |
| STATIC_ROOT | settings.py | `os.path.join(BASE_DIR, 'staticfiles')` |
| STATIC_URL | settings.py | `/static/` |
| whitenoise middleware | settings.py | 在 SecurityMiddleware 之後 |
| Procfile release | Railway | `collectstatic --noinput` |
| Procfile web | Railway | `gunicorn ... my_cabin.wsgi` |

---

## 快速參考

### Windows 本地開發
```powershell
.\venv\Scripts\Activate.ps1
python smart_cabin_project/manage.py runserver
# 訪問 http://127.0.0.1:8000
```

### Railway 部署
```bash
git add . && git commit -m "Fix" && git push
# Railway 自動部署、執行 collectstatic、啟動服務
```

---

## 技術細節

**為什麼 Windows 上不能用 gunicorn？**
- gunicorn 使用 Unix 特有的 `fcntl` 模塊
- Windows 需要使用 waitress、IIS HttpPlatformHandler 等替代方案
- Railway 的 Linux 環境支持 gunicorn

**為什麼要分離 release 和 web？**
- release 階段執行一次性任務（collectstatic）
- web 階段啟動服務（gunicorn）
- 確保靜態文件被收集後再啟動服務
