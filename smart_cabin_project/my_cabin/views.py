from pathlib import Path

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import requests
import datetime
import random
import time
from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Use Django's settings.BASE_DIR for path resolution
COMMENTS_FILE = os.path.join(settings.BASE_DIR, 'comments.txt')
BLACKLIST_FILE = os.path.join(settings.BASE_DIR, 'blacklist.txt')

# 隨機歡迎詞：網頁剛打開時給訪客的好印象
WELCOME_MESSAGES = [
    "您好！我是 FUTURE CABIN 導覽員，想了解小屋的哪個神奇功能呢？😊",
    "嗨！我是智慧導覽助手。日新國小團隊準備了很多驚喜，快問問我吧！✨"
]
AI_PROVIDER = os.environ.get('AI_PROVIDER', 'ollama').lower()
AI_API_URL = os.environ.get('AI_API_URL', 'http://127.0.0.1:11434/api/generate')
AI_MODEL_RAW = os.environ.get('AI_MODEL', 'qwen3.5-mini')
MODEL_ALIASES = {
    'gemma2b': 'gemma2:2b',
    'gpt-4': 'gpt-4',
}
AI_MODEL = MODEL_ALIASES.get(AI_MODEL_RAW.lower(), AI_MODEL_RAW)
AI_API_KEY = os.environ.get('AI_API_KEY', '')  # local Ollama usually does not require an API key
OLLAMA_LIKE_PROVIDERS = {'ollama', 'gemma2:2b', 'local'}
def get_ai_reply(prompt: str, retry_count: int = 2) -> str:
    if '127.0.0.1' in AI_API_URL or 'localhost' in AI_API_URL:
        return "導覽員：AI 服務目前無法連線，請稍後再試喔～ 😊"
    headers = {'Content-Type': 'application/json'}
    if AI_API_KEY:
        headers['Authorization'] = f'Bearer {AI_API_KEY}'

    if AI_PROVIDER in OLLAMA_LIKE_PROVIDERS:
        payload = {
            'model': AI_MODEL,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0.6,
                'top_p': 0.9,
                'num_threads': 1,
                'max_tokens': 400,
            }
        }
    else:
        payload = {
            'model': AI_MODEL,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.6,
            'max_tokens': 400,
        }

    # 重試機制
    for attempt in range(retry_count):
        try:
            response = requests.post(AI_API_URL, headers=headers, json=payload, timeout=90)
            if not response.ok:
                try:
                    error_body = response.json()
                    error_msg = error_body.get('error') or error_body.get('message') or str(error_body)
                except Exception:
                    error_msg = response.text or 'Unknown error'
                raise requests.exceptions.RequestException(
                    f'AI API error {response.status_code}: {error_msg}'
                )
            result = response.json()

            ai_reply = result.get('response') or result.get('text', '')
            if not ai_reply:
                choices = result.get('choices') or result.get('outputs') or []
                if isinstance(choices, list) and len(choices) > 0:
                    first = choices[0]
                    if isinstance(first, dict):
                        ai_reply = first.get('message', {}).get('content') or first.get('text') or first.get('output')
                        if not ai_reply:
                            ai_reply = first.get('content')
                    elif isinstance(first, str):
                        ai_reply = first
            if not ai_reply and isinstance(result.get('results'), list):
                for item in result['results']:
                    if isinstance(item, dict):
                        ai_reply = item.get('response') or item.get('content')
                        if ai_reply:
                            break
            return (ai_reply or '').strip()
        except requests.exceptions.Timeout:
            # 如果還有重試次數，等待後重試
            if attempt < retry_count - 1:
                time.sleep(2 ** attempt)  # 指數退避：2秒、4秒...
                continue
            else:
                raise
        except requests.exceptions.RequestException:
            # 其他請求錯誤也嘗試重試
            if attempt < retry_count - 1:
                time.sleep(1)
                continue
            else:
                raise

    return ''


def build_prompt(history, user_message: str) -> str:
    base = (
        "Role: 你是『FUTURE CABIN 智慧小屋』專業導覽員(日新國小團隊製作)。\n"
        "事實：小屋是瓦楞紙組裝的模型，不是鋼材或大建築。\n"
        "技術：Micro:bit控制、伺服馬達電動門、防火設施。\n"
        "規則：回答要熱情且簡單(不要太短，多於80少於100個字)，每次只講幾個重點，讓訪客可以連續追問。"
        " 保留對話脈絡，避免重複已說過的內容。\n"
    )
    for exchange in history[-5:]:
        base += f"訪客問：{exchange['user']}\n導覽員回答：{exchange['assistant']}\n"
    base += f"訪客問：{user_message}\n導覽員回答："
    return base


def load_guest_comments():
    comments = []
    if not os.path.exists(COMMENTS_FILE):
        return comments

    try:
        with open(COMMENTS_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
    except Exception:
        return comments

    if not content:
        return comments

    entries = [entry.strip() for entry in content.split('-' * 30) if entry.strip()]
    for entry in entries[::-1]:
        lines = [line.strip() for line in entry.splitlines() if line.strip()]
        if not lines:
            continue
        header = lines[0]
        timestamp = ''
        name = '熱心訪客'
        message = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ''
        try:
            if header.startswith('【') and '】來自' in header:
                ts_part, rest = header.split('】', 1)
                timestamp = ts_part.lstrip('【')
                if '來自' in rest:
                    _, rest = rest.split('來自', 1)
                if '：' in rest:
                    name, first_msg = rest.split('：', 1)
                    name = name.strip() if name.strip() else '熱心訪客'
                    if not message:
                        message = first_msg.strip()
                else:
                    name = rest.strip() or '熱心訪客'
                # 只在成功解析且有有效数据时才添加
                if timestamp and (message or name != '熱心訪客'):
                    comments.append({
                        'timestamp': timestamp,
                        'name': name,
                        'message': message
                    })
        except Exception:
            # 解析失败时跳过此条目
            continue
    return comments


def chat_view(request):
    """處理 AI 對話與首頁顯示"""
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'reply': '導覽員：請輸入問題喔！我隨時準備好為您介紹。'})

        history = request.session.get('chat_history', [])
        prompt = build_prompt(history, user_message)
        
        try:
            ai_reply = get_ai_reply(prompt)
            if ai_reply:
                history.append({'user': user_message, 'assistant': ai_reply})
                request.session['chat_history'] = history[-10:]
                request.session.modified = True
                return JsonResponse({'reply': ai_reply})
            else:
                return JsonResponse({'reply': '導覽員：無法獲得回應，請稍後再試。'})
        except Exception:
            return JsonResponse({'reply': '導覽員：服務暫時不可用，請稍後再試。'})

    context = {
        'team_name': '日新國小 智慧小屋團隊',
        'welcome_text': random.choice(WELCOME_MESSAGES),
        'guest_comments': load_guest_comments(),
    }
    return render(request, 'chat.html', context)


def check_ai_status(request):
    """檢查 AI 服務狀態"""
    try:
        test_prompt = "Hello"
        response = requests.post(
            AI_API_URL, 
            json={
                'model': AI_MODEL,
                'prompt': test_prompt,
                'stream': False
            },
            timeout=15
        )
        if response.status_code == 200:
            return JsonResponse({
                'status': 'ok',
                'provider': AI_PROVIDER,
                'model': AI_MODEL,
                'url': AI_API_URL
            })
        else:
            try:
                error_body = response.json()
                error_msg = error_body.get('error') or error_body.get('message') or str(error_body)
            except Exception:
                error_msg = response.text or 'Unknown error'
            return JsonResponse({
                'status': 'error',
                'message': f'AI服務返回 HTTP {response.status_code}: {error_msg}',
                'provider': AI_PROVIDER,
                'url': AI_API_URL
            })
    except requests.exceptions.ConnectionError:
        return JsonResponse({
            'status': 'error',
            'message': f'無法連接到 {AI_API_URL}，{AI_PROVIDER} 服務可能未運行',
            'url': AI_API_URL
        })
    except requests.exceptions.Timeout:
        return JsonResponse({
            'status': 'error',
            'message': f'連接 {AI_API_URL} 超時，服務可能過載或無響應',
            'url': AI_API_URL
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'provider': AI_PROVIDER
        })


@csrf_exempt
def feedback_view(request):
    """處理留言板存檔"""
    if request.method == 'POST':
        user_name = request.POST.get('name', '熱心訪客')
        user_msg = request.POST.get('message', '').strip()
        time_stamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        
        # 系統測試請求
        if user_name == 'system_check' and user_msg == '系統狀態檢查測試留言':
            return JsonResponse({'status': 'ok'})
        
        if not user_msg:
            return JsonResponse({'status': 'error', 'message': '請填寫留言內容'})
        
        try:
            # Ensure the directory exists
            comments_dir = os.path.dirname(COMMENTS_FILE)
            os.makedirs(comments_dir, exist_ok=True)
            # Write to comments.txt safely
            with open(COMMENTS_FILE, 'a', encoding='utf-8') as f:
                f.write(f"【{time_stamp}】來自 {user_name}：{user_msg}\n" + "-"*30 + "\n")
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'fail'}, status=400)


def check_view(request):
    """系統狀態檢查頁面"""
    context = {
        'team_name': '日新國小 智慧小屋團隊',
    }
    return render(request, 'check.html', context)


def redirect_to_check(request):
    """根路徑重定向到獨立的系統檢查頁面"""
    return redirect('/check/')


def admin_view(request):
    """管理員頁面"""
    password = request.GET.get('pwd', '')
    if password != 'admin2024':
        return JsonResponse({'error': '未授權'}, status=401)
    
    context = {
        'team_name': '日新國小 智慧小屋團隊',
    }
    return render(request, 'admin.html', context)


def api_admin_stats(request):
    """API: 獲取管理員統計數據"""
    password = request.GET.get('pwd', '')
    if password != 'admin2024':
        return JsonResponse({'error': '未授權'}, status=401)
    
    comments_data = load_guest_comments()
    total_comments = len(comments_data)
    
    comments_by_date = {}
    for comment in comments_data:
        date = comment['timestamp'].split()[0] if comment['timestamp'] else '未知'
        if date not in comments_by_date:
            comments_by_date[date] = 0
        comments_by_date[date] += 1
    
    system_status = {
        'ollama': check_ollama_status(),
        'django': True,
    }
    
    visitor_names = {}
    for comment in comments_data:
        name = comment['name']
        if name not in visitor_names:
            visitor_names[name] = 0
        visitor_names[name] += 1
    
    top_visitors = sorted(visitor_names.items(), key=lambda x: x[1], reverse=True)
    
    blacklist = load_blacklist()
    
    sorted_dates = sorted(comments_by_date.keys())
    chart_data = {
        'dates': sorted_dates,
        'counts': [comments_by_date[date] for date in sorted_dates]
    }
    
    return JsonResponse({
        'total_comments': total_comments,
        'unique_visitors': len(visitor_names),
        'comments_by_date': comments_by_date,
        'chart_data': chart_data,
        'top_visitors': top_visitors[:10],
        'system_status': system_status,
        'latest_comments': comments_data[:20],
        'blacklist': blacklist,
    })


def check_ollama_status():
    """檢查 AI 服務狀態"""
    try:
        response = requests.post(
            AI_API_URL,
            json={
                'model': AI_MODEL,
                'prompt': 'test',
                'stream': False,
                'options': {
                    'temperature': 0.6,
                    'top_p': 0.9,
                    'num_threads': 1,
                    'max_tokens': 50,
                }
            },
            timeout=10
        )
        return response.status_code == 200
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        return False
    except Exception:
        return False


@csrf_exempt
def api_delete_comment(request):
    """API: 刪除留言 - 支持按時間戳和名字刪除"""
    if request.method != 'POST':
        return JsonResponse({'error': '方法不允許'}, status=405)
    
    password = request.POST.get('pwd', '')
    if password != 'admin2024':
        return JsonResponse({'error': '未授權'}, status=401)
    
    comment_timestamp = request.POST.get('timestamp', '')
    comment_name = request.POST.get('name', '')
    
    try:
        # Read comments safely
        try:
            with open(COMMENTS_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            return JsonResponse({'error': '找不到留言檔案'}, status=404)
        
        new_lines = []
        i = 0
        found = False
        
        while i < len(lines):
            line = lines[i]
            if comment_timestamp in line and f'來自 {comment_name}：' in line:
                found = True
                i += 1
                while i < len(lines) and (lines[i].strip().startswith('-') or not lines[i].strip()):
                    i += 1
                continue
            else:
                new_lines.append(line)
                i += 1
        
        if not found:
            return JsonResponse({'error': '找不到留言'}, status=404)
        
        with open(COMMENTS_FILE, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        return JsonResponse({'status': 'ok', 'message': '留言已刪除'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def load_blacklist():
    """加載黑名單"""
    if not os.path.exists(BLACKLIST_FILE):
        return []
    try:
        with open(BLACKLIST_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        # Treat missing file as empty blacklist
        return []
    except Exception:
        return []


@csrf_exempt
def api_ban_visitor(request):
    """API: 踢出/封禁訪客"""
    if request.method != 'POST':
        return JsonResponse({'error': '方法不允許'}, status=405)
    
    password = request.POST.get('pwd', '')
    if password != 'admin2024':
        return JsonResponse({'error': '未授權'}, status=401)
    
    visitor_name = request.POST.get('name', '').strip()
    if not visitor_name:
        return JsonResponse({'error': '訪客名稱不能為空'}, status=400)
    
    try:
        blacklist = load_blacklist()
        if visitor_name not in blacklist:
            # Ensure directory exists before writing
            blacklist_dir = os.path.dirname(BLACKLIST_FILE)
            os.makedirs(blacklist_dir, exist_ok=True)
            with open(BLACKLIST_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{visitor_name}\n")
        
        # Remove all comments from this visitor
        comments = load_guest_comments()
        try:
            with open(COMMENTS_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []
        
        new_lines = []
        skip_block = False
        for line in lines:
            if f'來自 {visitor_name}：' in line:
                skip_block = True
                continue
            elif skip_block and line.strip().startswith('-' * 20):
                skip_block = False
                continue
            elif not skip_block:
                new_lines.append(line)
        
        with open(COMMENTS_FILE, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        return JsonResponse({'status': 'ok', 'message': f'已踢出訪客: {visitor_name}'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def api_unban_visitor(request):
    """API: 解除訪客封禁"""
    if request.method != 'POST':
        return JsonResponse({'error': '方法不允許'}, status=405)
    
    password = request.POST.get('pwd', '')
    if password != 'admin2024':
        return JsonResponse({'error': '未授權'}, status=401)
    
    visitor_name = request.POST.get('name', '').strip()
    if not visitor_name:
        return JsonResponse({'error': '訪客名稱不能為空'}, status=400)
    
    try:
        blacklist = load_blacklist()
        if visitor_name in blacklist:
            blacklist.remove(visitor_name)
            with open(BLACKLIST_FILE, 'w', encoding='utf-8') as f:
                for name in blacklist:
                    f.write(f"{name}\n")
        
        return JsonResponse({'status': 'ok', 'message': f'已解除訪客封禁: {visitor_name}'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def api_get_blacklist(request):
    """API: 獲取黑名單"""
    password = request.GET.get('pwd', '')
    if password != 'admin2024':
        return JsonResponse({'error': '未授權'}, status=401)
    
    blacklist = load_blacklist()
    return JsonResponse({'blacklist': blacklist})
