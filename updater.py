import requests  
import json  
import webbrowser  
import tkinter as tk  
from tkinter import messagebox  

def check_for_updates(current_version, owner, repo):  
    """  
    检查GitHub上是否有新版本可用  
    
    参数:  
        current_version: 当前版本号 (如 "1.0.0")  
        owner: GitHub用户名/组织名  
        repo: 仓库名称  
    
    返回:  
        (has_update, latest_version, download_url, changelog)  
    """  
    try:  
        # 访问GitHub API获取最新版本  
        api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"  
        response = requests.get(api_url)  
        
        if response.status_code != 200:  
            print(f"API请求失败，状态码: {response.status_code}")  
            return False, current_version, "", ""  
        
        release_data = json.loads(response.text)  
        latest_version = release_data['tag_name'].lstrip('v')  # 移除版本号前的'v'  
        
        # 简单地比较版本号（这种方法对标准的语义化版本号有效）  
        current_parts = [int(x) for x in current_version.split('.')]  
        latest_parts = [int(x) for x in latest_version.split('.')]  
        
        has_update = False  
        for i in range(max(len(current_parts), len(latest_parts))):  
            current_part = current_parts[i] if i < len(current_parts) else 0  
            latest_part = latest_parts[i] if i < len(latest_parts) else 0  
            
            if latest_part > current_part:  
                has_update = True  
                break  
            elif current_part > latest_part:  
                break  
        
        # 如果有新版本，获取下载链接（通常是第一个资源文件）  
        download_url = ""  
        if has_update and 'assets' in release_data and len(release_data['assets']) > 0:  
            download_url = release_data['assets'][0]['browser_download_url']  
        
        # 获取更新日志  
        changelog = release_data.get('body', '')  
        
        return has_update, latest_version, download_url, changelog  
    
    except Exception as e:  
        print(f"检查更新时出错: {e}")  
        return False, current_version, "", ""  

def show_update_dialog(root, current_version, latest_version, download_url, changelog):  
    """显示更新对话框"""  
    dialog = tk.Toplevel(root)  
    dialog.title("发现新版本")  
    dialog.geometry("400x300")  
    dialog.resizable(False, False)  
    dialog.transient(root)  # 设置为模态窗口  
    dialog.grab_set()  
    
    # 对话框内容  
    tk.Label(dialog, text=f"当前版本: v{current_version}", anchor="w").pack(fill=tk.X, padx=20, pady=(20,5))  
    tk.Label(dialog, text=f"最新版本: v{latest_version}", anchor="w").pack(fill=tk.X, padx=20, pady=5)  
    
    # 更新日志框  
    tk.Label(dialog, text="更新内容:", anchor="w").pack(fill=tk.X, padx=20, pady=(15,5))  
    changelog_text = tk.Text(dialog, height=8, wrap=tk.WORD)  
    changelog_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)  
    changelog_text.insert(tk.END, changelog)  
    changelog_text.config(state=tk.DISABLED)  # 设为只读  
    
    # 按钮区域  
    button_frame = tk.Frame(dialog)  
    button_frame.pack(fill=tk.X, padx=20, pady=20)  
    
    tk.Button(button_frame, text="立即更新",   
              command=lambda: open_download_page(download_url, dialog)).pack(side=tk.LEFT, padx=5)  
    tk.Button(button_frame, text="稍后更新",   
              command=dialog.destroy).pack(side=tk.RIGHT, padx=5)  

def open_download_page(url, dialog=None):  
    """打开下载页面"""  
    webbrowser.open(url)  
    if dialog:  
        dialog.destroy()