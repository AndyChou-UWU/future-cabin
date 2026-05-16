from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views # 只有當 urls.py 跟 views.py 在同一個資料夾時才用這個

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.redirect_to_check, name='index'),          # 根路徑重定向到系統檢查
    path('chat/', views.chat_view, name='chat'),              # AI 聊天系統
    path('check/', views.check_view, name='check'),           # 系統狀態檢查
    path('feedback/', views.feedback_view, name='feedback'),  # 留言板功能
    path('api/check-ai/', views.check_ai_status, name='check_ai_status'),  # AI 狀態檢查
    path('admin-panel/', views.admin_view, name='admin_panel'),  # 管理員面板
    path('api/admin-stats/', views.api_admin_stats, name='api_admin_stats'),  # 管理員統計 API
    path('api/delete-comment/', views.api_delete_comment, name='api_delete_comment'),  # 刪除留言
    path('api/ban-visitor/', views.api_ban_visitor, name='api_ban_visitor'),  # 封禁訪客
    path('api/unban-visitor/', views.api_unban_visitor, name='api_unban_visitor'),  # 解除封禁
    path('api/get-blacklist/', views.api_get_blacklist, name='api_get_blacklist'),  # 獲取黑名單
]

# 在開發模式下服務根目錄的靜態文件
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])