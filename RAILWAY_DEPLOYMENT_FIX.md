# Railway 部署靜態資源修復方案

## 問題診斷
您的應用在 Railway 上靜態資源無法加載，主要原因有：

1. **Procfile 配置錯誤** - `--chdir` 參數破壞了工作目錄結構
2. **缺少 collectstatic 步驟** - Railway 部署時沒有自動收集靜態文件
3. **WSGI 模組路徑混亂** - 不同文件中的 Django 設置路徑不一致

---

## 已修復的檔案

### 1. ✅ Procfile (最關鍵)
**問題：**
```
web: gunicorn --chdir smart_cabin_project --pythonpath . smart_cabin_project.wsgi --log-file -
```

**修復為：**
```
release: python smart_cabin_project/manage.py collectstatic --noinput
web: gunicorn -w 4 -b 0.0.0.0:$PORT smart_cabin_project.my_cabin.wsgi --log-file -
```

**改動說明：**
- `release` 命令在部署時自動執行 collectstatic
- 移除有害的 `--chdir` 參數
- 修正 WSGI 應用的完整模組路徑
- 使用 `$PORT` 環境變數（Railway 自動提供）

---

### 2. ✅ smart_cabin_project/my_cabin/wsgi.py
**修復為正確的模組路徑：**
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_cabin.settings')
```

---

### 3. ✅ wsgi_entry.py
**修復為簡潔的配置：**
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_cabin.settings')
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'smart_cabin_project'))
```

---

### 4. ✅ settings.py
**調整：**
- 設定 `CSRF_COOKIE_SECURE = False` 和 `SESSION_COOKIE_SECURE = False`（Railway 環境）
- 新增 WhiteNoise 優化配置

---

## 部署步驟

### 本地測試（推薦）
```bash
# 清理舊的靜態文件
python smart_cabin_project/manage.py collectstatic --clear --noinput

# 測試 gunicorn
gunicorn -w 4 -b 127.0.0.1:8000 smart_cabin_project.my_cabin.wsgi
```

訪問 `http://localhost:8000` 查看靜態資源是否正常加載

### 推送到 Railway
```bash
git add .
git commit -m "Fix static files loading for Railway deployment"
git push
```

---

## 驗證清單

- [ ] Railway 部署完成後檢查瀏覽器開發工具的 Network 標籤
- [ ] CSS 和 JavaScript 文件的狀態碼應為 200（不是 404）
- [ ] 頁面樣式正確顯示
- [ ] 如有圖像，確認已正常加載

---

## 如果還有問題

1. **檢查 Railway 日誌**：
   ```
   Railway Dashboard > Deployment > Logs
   ```

2. **驗證 collectstatic 是否執行**：查看部署日誌中是否有 `collectstatic` 輸出

3. **檢查 staticfiles 目錄**：確保本地的 `staticfiles/` 文件夾包含了所有靜態文件

4. **清除 Railway 緩存**：在 Railway Dashboard 中重新部署（Redeploy）

---

## 其他最佳實踐

- 確保 `requirements.txt` 包含 `whitenoise`：`pip list | grep whitenoise`
- 在 Railway 中設置環境變數：`DJANGO_DEBUG=False`
- 使用 CDN 服務（如 Cloudflare）進一步加速靜態資源
