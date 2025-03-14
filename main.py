import tkinter as tk  
from tkinter import ttk, scrolledtext, messagebox  
import re  
import pyperclip  # 用于复制到剪贴板  
from updater import check_for_updates, show_update_dialog  
 
# 定义版本号  
APP_VERSION = "2.1.0"  
GITHUB_OWNER = "Guowei-Shopee"  # 替换为您实际的GitHub用户名  
GITHUB_REPO = "order-processor"    # 替换为您实际计划使用的仓库名 


class OrderProcessorApp:  
    def __init__(self, root):  
        self.root = root  
        self.root.title(f"订单处理工具 v{APP_VERSION}")   
        self.root.geometry("900x650")  # 调整窗口大小以适应新增控件  
        
        # 创建主框架  
        main_frame = ttk.Frame(root, padding="10")  
        main_frame.pack(fill=tk.BOTH, expand=True)  
        
        # 输入区域  
        input_frame = ttk.LabelFrame(main_frame, text="请粘贴订单数据", padding="10")  
        input_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)  
        
        self.input_text = scrolledtext.ScrolledText(input_frame, height=10)  
        self.input_text.pack(fill=tk.BOTH, expand=True)  
        
        # 输出格式选择区域  
        options_frame = ttk.Frame(main_frame)  
        options_frame.pack(fill=tk.X, padx=5, pady=5)  
        
        # 输出格式选择  
        format_frame = ttk.LabelFrame(options_frame, text="输出选项", padding="10")  
        format_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)  
        
        self.output_option = tk.StringVar(value="auto")  
        ttk.Radiobutton(format_frame, text="智能检测 (自动输出所有匹配单号)", variable=self.output_option,   
                      value="auto").pack(side=tk.LEFT, padx=15)  
        ttk.Radiobutton(format_frame, text="仅输出SLS单号", variable=self.output_option,   
                      value="sls_only").pack(side=tk.LEFT, padx=15)  
        ttk.Radiobutton(format_frame, text="仅输出订单编号", variable=self.output_option,   
                      value="order_only").pack(side=tk.LEFT, padx=15)  
        
        # 功能按钮区域  
        button_frame = ttk.Frame(main_frame, padding="10")  
        button_frame.pack(fill=tk.X, padx=5)  
        
        ttk.Button(button_frame, text="格式整理", command=self.format_organization).pack(side=tk.LEFT, padx=5)  
        ttk.Button(button_frame, text="批量查订单格式", command=self.batch_query_format).pack(side=tk.LEFT, padx=5)  
        ttk.Button(button_frame, text="批量跑数据格式", command=self.batch_data_format).pack(side=tk.LEFT, padx=5)  
        ttk.Button(button_frame, text="复制结果", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)  
        ttk.Button(button_frame, text="清空", command=self.clear_all).pack(side=tk.RIGHT, padx=5)  
        
        # 输出区域  
        output_frame = ttk.LabelFrame(main_frame, text="处理结果", padding="10")  
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)  
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15)  
        self.output_text.pack(fill=tk.BOTH, expand=True)  
        
        # 状态栏和统计信息  
        stats_frame = ttk.Frame(main_frame)  
        stats_frame.pack(fill=tk.X, padx=5, pady=2)  
        
        self.stats_var = tk.StringVar()  
        self.stats_var.set("SLS单号: 0 | 订单编号: 0 | 未知单号: 0")  
        ttk.Label(stats_frame, textvariable=self.stats_var).pack(side=tk.LEFT)  
        
        self.status_var = tk.StringVar()  
        self.status_var.set("就绪")  
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)  
        status_bar.pack(fill=tk.X, padx=5, pady=2)  
        
        # 添加菜单栏  
        self.create_menu()  
                
        # 初始化后检查更新（延迟2秒，让界面先加载完毕）  
        self.root.after(2000, self.check_for_updates)  

    def create_menu(self):  
        """创建菜单栏"""  
        menubar = tk.Menu(self.root)  
        
        # 文件菜单  
        file_menu = tk.Menu(menubar, tearoff=0)  
        file_menu.add_command(label="清空", command=self.clear_all)  
        file_menu.add_separator()  
        file_menu.add_command(label="退出", command=self.root.quit)  
        menubar.add_cascade(label="文件", menu=file_menu)  
        
        # 帮助菜单  
        help_menu = tk.Menu(menubar, tearoff=0)  
        help_menu.add_command(label="检查更新", command=self.check_for_updates)  
        help_menu.add_command(label="关于", command=self.show_about)  
        menubar.add_cascade(label="帮助", menu=help_menu)  
        
        self.root.config(menu=menubar)  

    def check_for_updates(self):  
        """检查更新"""  
        has_update, latest_version, download_url, changelog = check_for_updates(  
            APP_VERSION, GITHUB_OWNER, GITHUB_REPO  
        )  
        
        if has_update and download_url:  
            show_update_dialog(  
                self.root, APP_VERSION, latest_version, download_url, changelog  
            )  

    def show_about(self):  
        """显示关于对话框"""  
        messagebox.showinfo(  
            "关于订单处理工具",   
            f"订单处理工具 v{APP_VERSION}\n\n"  
            "一个高效的订单号提取和格式化工具\n\n"  
            "© 2025 Guowei Huang"  
        )  

    def extract_order_numbers(self, text):  
        """提取SLS单号、订单编号和未知单号"""  
        # SLS单号模式:   
        # MX/CL/CO是18位单号(国家代码2位+16位字符)  
        # 其他国家代码(BR/MY/PH/SG/TH/TW/VN)仍为15位(国家代码2位+13位字符)  
        sls_pattern = r'(?:MX|CL|CO)[A-Za-z0-9]{16}|(?:BR|MY|PH|SG|TH|TW|VN)[A-Za-z0-9]{13}'  
        
        # 查找所有SLS单号匹配项  
        sls_matches = re.findall(sls_pattern, text)  
        
        # 创建一个新的文本副本，将所有SLS单号替换为空格，以避免重复匹配  
        filtered_text = text  
        for sls in sls_matches:  
            filtered_text = filtered_text.replace(sls, ' ' * len(sls))  
        
        # 订单编号模式: 6位数字开头 + 8-9位字母数字混合字符，且要求必须至少包含一个字母  
        order_pattern = r'\d{6}(?=.*[A-Za-z])[A-Za-z0-9]{8,9}'  
        
        # 在过滤后的文本中查找订单编号  
        order_matches = re.findall(order_pattern, filtered_text)  
        
        # 再次过滤文本，将订单编号也替换为空格  
        for order in order_matches:  
            filtered_text = filtered_text.replace(order, ' ' * len(order))  
            
        # 提取未知单号，进行逐个处理以避免重叠匹配  
        unknown_matches = []  
        
        # 持续搜索直到没有新的匹配  
        while True:  
            # 提取至少8位的字母数字组合  
            unknown_pattern = r'[A-Za-z0-9]{8,}'  
            match = re.search(unknown_pattern, filtered_text)  
            
            # 如果没有找到匹配项，退出循环  
            if not match:  
                break  
                
            # 获取匹配的文本  
            item = match.group(0)  
            
            # 检查是否是纯数字  
            is_pure_digits = item.isdigit()  
            
            # 检查是否包含大写字母和数字的组合（不含小写字母）  
            has_uppercase = any(char.isupper() for char in item)  
            has_digit = any(char.isdigit() for char in item)  
            has_lowercase = any(char.islower() for char in item)  
            is_uppercase_with_digits = has_uppercase and has_digit and not has_lowercase  
            
            # 如果符合条件，添加到结果列表  
            if is_pure_digits or is_uppercase_with_digits:  
                unknown_matches.append(item)  
            
            # 无论是否符合条件，都从文本中移除当前匹配项以避免重复匹配  
            start, end = match.span()  
            filtered_text = filtered_text[:start] + ' ' * (end - start) + filtered_text[end:]  
        
        # 更新统计信息  
        self.stats_var.set(f"SLS单号: {len(sls_matches)} | 订单编号: {len(order_matches)} | 未知单号: {len(unknown_matches)}")  
        
        return {"sls": sls_matches, "order": order_matches, "unknown": unknown_matches}
    
    def get_filtered_data(self, data):  
        """根据用户选择过滤数据"""  
        output_option = self.output_option.get()  
        
        sls_numbers = data["sls"]  
        order_numbers = data["order"]  
        unknown_numbers = data["unknown"]  
        
        # 统计检测到的单号类型  
        has_sls = len(sls_numbers) > 0  
        has_order = len(order_numbers) > 0  
        has_unknown = len(unknown_numbers) > 0  
        
        if output_option == "sls_only":  
            # 仅保留SLS单号  
            sls_numbers = data["sls"]  
            order_numbers = []  
            unknown_numbers = []  
        elif output_option == "order_only":  
            # 仅保留订单编号  
            sls_numbers = []  
            order_numbers = data["order"]  
            unknown_numbers = []  
        # 自动模式 (auto) 使用所有检测到的单号  
        
        return {  
            "sls": sls_numbers,   
            "order": order_numbers,  
            "unknown": unknown_numbers,  
            "has_sls": has_sls,  
            "has_order": has_order,  
            "has_unknown": has_unknown  
        }  
        
    def format_organization(self):  
        """格式整理功能：按excel格式竖排列整理"""  
        input_text = self.input_text.get("1.0", tk.END)  
        raw_data = self.extract_order_numbers(input_text)  
        filtered_data = self.get_filtered_data(raw_data)  
        
        sls_numbers = filtered_data["sls"]  
        order_numbers = filtered_data["order"]  
        unknown_numbers = filtered_data["unknown"]  
        
        has_sls = filtered_data["has_sls"]  
        has_order = filtered_data["has_order"]  
        has_unknown = filtered_data["has_unknown"]  
        
        # 智能输出布局决策  
        # 如果同时存在多种单号，使用多列布局  
        # 如果只有一种单号，使用单列布局  
        column_count = sum([1 if sls_numbers else 0,   
                          1 if order_numbers else 0,   
                          1 if unknown_numbers and self.output_option.get() == "auto" else 0])  
        
        using_multi_columns = column_count > 1  
        
        if using_multi_columns:  
            # 多列输出模式 (可能是A/B列或A/B/C列)  
            max_rows = max(len(sls_numbers) if sls_numbers else 0,   
                         len(order_numbers) if order_numbers else 0,  
                         len(unknown_numbers) if unknown_numbers else 0)  
            result_rows = []  
            
            for i in range(max_rows):  
                sls_value = sls_numbers[i] if sls_numbers and i < len(sls_numbers) else ""  
                order_value = order_numbers[i] if order_numbers and i < len(order_numbers) else ""  
                unknown_value = unknown_numbers[i] if unknown_numbers and i < len(unknown_numbers) else ""  
                
                if column_count == 3:  
                    # A/B/C三列  
                    result_rows.append(f"{sls_value}\t{order_value}\t{unknown_value}")  
                else:  
                    # A/B两列  
                    if sls_numbers and order_numbers:  
                        result_rows.append(f"{sls_value}\t{order_value}")  
                    elif sls_numbers and unknown_numbers:  
                        result_rows.append(f"{sls_value}\t{unknown_value}")  
                    elif order_numbers and unknown_numbers:  
                        result_rows.append(f"{order_value}\t{unknown_value}")  
                
            result = "\n".join(result_rows)  
            count = len(sls_numbers) + len(order_numbers) + len(unknown_numbers)  
            
            if column_count == 3:  
                output_desc = "SLS单号、订单编号和未知单号 (A/B/C列)"  
            elif sls_numbers and order_numbers:  
                output_desc = "SLS单号和订单编号 (A/B列)"  
            elif sls_numbers and unknown_numbers:  
                output_desc = "SLS单号和未知单号 (A/B列)"  
            else:  
                output_desc = "订单编号和未知单号 (A/B列)"  
        else:  
            # 单列输出  
            if sls_numbers:  
                all_numbers = sls_numbers  
                output_desc = "SLS单号"  
            elif order_numbers:  
                all_numbers = order_numbers  
                output_desc = "订单编号"   
            elif unknown_numbers:  
                all_numbers = unknown_numbers  
                output_desc = "未知单号"  
            else:  
                all_numbers = []  
                output_desc = "单号"  
                
            result = "\n".join(all_numbers)  
            count = len(all_numbers)  
        
        self.output_text.delete("1.0", tk.END)  
        self.output_text.insert("1.0", result)  
        
        # 更新状态栏  
        self.status_var.set(f"已整理 {count} 个{output_desc}")  
    
    def batch_query_format(self):  
        """批量查订单格式：每个订单号后添加逗号，最后一个除外"""  
        input_text = self.input_text.get("1.0", tk.END)  
        raw_data = self.extract_order_numbers(input_text)  
        filtered_data = self.get_filtered_data(raw_data)  
        
        sls_numbers = filtered_data["sls"]  
        order_numbers = filtered_data["order"]  
        unknown_numbers = filtered_data["unknown"]  
        
        has_sls = filtered_data["has_sls"]  
        has_order = filtered_data["has_order"]  
        has_unknown = filtered_data["has_unknown"]  
        
        # 智能输出布局决策  
        column_count = sum([1 if sls_numbers else 0,   
                          1 if order_numbers else 0,   
                          1 if unknown_numbers and self.output_option.get() == "auto" else 0])  
        
        using_multi_columns = column_count > 1  
        
        if using_multi_columns:  
            # 多列输出处理 - 分别处理各类单号  
            result_parts = []  
            total_count = 0  
            
            if sls_numbers:  
                sls_temp = [num + "," for num in sls_numbers[:-1]]  
                sls_temp.append(sls_numbers[-1])  
                sls_formatted = "".join(sls_temp)  
                result_parts.append(f"SLS单号:\n{sls_formatted}")  
                total_count += len(sls_numbers)  
                
            if order_numbers:  
                order_temp = [num + "," for num in order_numbers[:-1]]  
                order_temp.append(order_numbers[-1])  
                order_formatted = "".join(order_temp)  
                result_parts.append(f"订单编号:\n{order_formatted}")  
                total_count += len(order_numbers)  
            
            if unknown_numbers and self.output_option.get() == "auto":  
                unknown_temp = [num + "," for num in unknown_numbers[:-1]]  
                unknown_temp.append(unknown_numbers[-1])  
                unknown_formatted = "".join(unknown_temp)  
                result_parts.append(f"未知单号:\n{unknown_formatted}")  
                total_count += len(unknown_numbers)  
                
            result = "\n\n".join(result_parts)  
            count = total_count  
            
            if column_count == 3:  
                output_desc = "SLS单号、订单编号和未知单号 (分组显示)"  
            elif sls_numbers and order_numbers:  
                output_desc = "SLS单号和订单编号 (分组显示)"  
            elif sls_numbers and unknown_numbers:  
                output_desc = "SLS单号和未知单号 (分组显示)"  
            else:  
                output_desc = "订单编号和未知单号 (分组显示)"  
        else:  
            # 单列输出  
            if sls_numbers:  
                all_numbers = sls_numbers  
                output_desc = "SLS单号"  
            elif order_numbers:  
                all_numbers = order_numbers  
                output_desc = "订单编号"   
            elif unknown_numbers:  
                all_numbers = unknown_numbers  
                output_desc = "未知单号"  
            else:  
                all_numbers = []  
                output_desc = "单号"  
            
            if all_numbers:  
                # 除最后一个外，所有订单号后添加逗号  
                formatted_numbers = [num + "," for num in all_numbers[:-1]]  
                formatted_numbers.append(all_numbers[-1])  # 添加最后一个（不带逗号）  
                result = "".join(formatted_numbers)  
                count = len(all_numbers)  
            else:  
                result = ""  
                count = 0  
        
        self.output_text.delete("1.0", tk.END)  
        self.output_text.insert("1.0", result)  
        
        # 更新状态栏  
        self.status_var.set(f"已处理 {count} 个{output_desc}为批量查询格式")  
    
    def batch_data_format(self):  
        """批量跑数据格式：'订单号',格式"""  
        input_text = self.input_text.get("1.0", tk.END)  
        raw_data = self.extract_order_numbers(input_text)  
        filtered_data = self.get_filtered_data(raw_data)  
        
        sls_numbers = filtered_data["sls"]  
        order_numbers = filtered_data["order"]  
        unknown_numbers = filtered_data["unknown"]  
        
        has_sls = filtered_data["has_sls"]  
        has_order = filtered_data["has_order"]  
        has_unknown = filtered_data["has_unknown"]  
        
        # 智能输出布局决策  
        column_count = sum([1 if sls_numbers else 0,   
                          1 if order_numbers else 0,   
                          1 if unknown_numbers and self.output_option.get() == "auto" else 0])  
        
        using_multi_columns = column_count > 1  
        
        if using_multi_columns:  
            # 多列输出处理 - 分别处理各类单号  
            result_parts = []  
            total_count = 0  
            
            if sls_numbers:  
                sls_temp = [f"'{num}'," for num in sls_numbers[:-1]]  
                sls_temp.append(f"'{sls_numbers[-1]}'")  
                sls_formatted = "".join(sls_temp)  
                result_parts.append(f"SLS单号:\n{sls_formatted}")  
                total_count += len(sls_numbers)  
                
            if order_numbers:  
                order_temp = [f"'{num}'," for num in order_numbers[:-1]]  
                order_temp.append(f"'{order_numbers[-1]}'")  
                order_formatted = "".join(order_temp)  
                result_parts.append(f"订单编号:\n{order_formatted}")  
                total_count += len(order_numbers)  
            
            if unknown_numbers and self.output_option.get() == "auto":  
                unknown_temp = [f"'{num}'," for num in unknown_numbers[:-1]]  
                unknown_temp.append(f"'{unknown_numbers[-1]}'")  
                unknown_formatted = "".join(unknown_temp)  
                result_parts.append(f"未知单号:\n{unknown_formatted}")  
                total_count += len(unknown_numbers)  
                
            result = "\n\n".join(result_parts)  
            count = total_count  
            
            if column_count == 3:  
                output_desc = "SLS单号、订单编号和未知单号 (分组显示)"  
            elif sls_numbers and order_numbers:  
                output_desc = "SLS单号和订单编号 (分组显示)"  
            elif sls_numbers and unknown_numbers:  
                output_desc = "SLS单号和未知单号 (分组显示)"  
            else:  
                output_desc = "订单编号和未知单号 (分组显示)"  
        else:  
            # 单列输出  
            if sls_numbers:  
                all_numbers = sls_numbers  
                output_desc = "SLS单号"  
            elif order_numbers:  
                all_numbers = order_numbers  
                output_desc = "订单编号"   
            elif unknown_numbers:  
                all_numbers = unknown_numbers  
                output_desc = "未知单号"  
            else:  
                all_numbers = []  
                output_desc = "单号"  
            
            if all_numbers:  
                # 所有订单号格式化为'订单号',  
                formatted_numbers = [f"'{num}'," for num in all_numbers[:-1]]  
                # 最后一个不加逗号  
                formatted_numbers.append(f"'{all_numbers[-1]}'")  
                result = "".join(formatted_numbers)  
                count = len(all_numbers)  
            else:  
                result = ""  
                count = 0  
        
        self.output_text.delete("1.0", tk.END)  
        self.output_text.insert("1.0", result)  
        
        # 更新状态栏  
        self.status_var.set(f"已处理 {count} 个{output_desc}为批量数据格式")  
    
    def copy_to_clipboard(self):  
        """复制结果到剪贴板"""  
        output_text = self.output_text.get("1.0", tk.END).strip()  
        if output_text:  
            pyperclip.copy(output_text)  
            self.status_var.set("结果已复制到剪贴板")  
        else:  
            self.status_var.set("没有可复制的内容")  
    
    def clear_all(self):  
        """清空输入和输出文本区域"""  
        self.input_text.delete("1.0", tk.END)  
        self.output_text.delete("1.0", tk.END)  
        self.status_var.set("已清空")  
        self.stats_var.set("SLS单号: 0 | 订单编号: 0 | 未知单号: 0")  

def main():  
    root = tk.Tk()  
    app = OrderProcessorApp(root)  
    root.mainloop()  

if __name__ == "__main__":  
    main()