import tkinter as tk  
from tkinter import ttk, scrolledtext  
import re  
import pyperclip  # 用于复制到剪贴板  

class OrderProcessorApp:  
    def __init__(self, root):  
        self.root = root  
        self.root.title("订单处理工具")  
        self.root.geometry("900x650")  # 调整窗口大小以适应新增控件  
        
        # 创建主框架  
        main_frame = ttk.Frame(root, padding="10")  
        main_frame.pack(fill=tk.BOTH, expand=True)  
        
        # 输入区域  
        input_frame = ttk.LabelFrame(main_frame, text="请粘贴订单数据", padding="10")  
        input_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)  
        
        self.input_text = scrolledtext.ScrolledText(input_frame, height=10)  
        self.input_text.pack(fill=tk.BOTH, expand=True)  
        
        # 订单类型和输出格式选择区域  
        options_frame = ttk.Frame(main_frame)  
        options_frame.pack(fill=tk.X, padx=5, pady=5)  
        
        # 订单类型选择  
        type_frame = ttk.LabelFrame(options_frame, text="选择订单类型", padding="10")  
        type_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))  
        
        self.order_type = tk.StringVar(value="both")  
        ttk.Radiobutton(type_frame, text="仅SLS单号", variable=self.order_type,   
                        value="sls").pack(side=tk.LEFT, padx=15)  
        ttk.Radiobutton(type_frame, text="仅订单编号", variable=self.order_type,   
                        value="order").pack(side=tk.LEFT, padx=15)  
        ttk.Radiobutton(type_frame, text="两者都处理", variable=self.order_type,   
                        value="both").pack(side=tk.LEFT, padx=15)  
        
        # 输出格式选择  
        format_frame = ttk.LabelFrame(options_frame, text="输出格式", padding="10")  
        format_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))  
        
        self.output_format = tk.StringVar(value="column")  
        ttk.Radiobutton(format_frame, text="单列输出", variable=self.output_format,   
                      value="single").pack(side=tk.LEFT, padx=15)  
        ttk.Radiobutton(format_frame, text="双列输出(A/B列)", variable=self.output_format,   
                      value="column").pack(side=tk.LEFT, padx=15)  
        
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
        self.stats_var.set("SLS单号: 0 | 订单编号: 0")  
        ttk.Label(stats_frame, textvariable=self.stats_var).pack(side=tk.LEFT)  
        
        self.status_var = tk.StringVar()  
        self.status_var.set("就绪")  
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)  
        status_bar.pack(fill=tk.X, padx=5, pady=2)  
        
    def extract_order_numbers(self, text):  
        """提取SLS单号和订单编号，根据用户选择返回不同结果"""  
        # SLS单号模式: 以指定的双字母开头(BR/CL/CO/MX/MY/PH/SG/TH/TW/VN)加上13个字母数字字符  
        sls_pattern = r'(?:BR|CL|CO|MX|MY|PH|SG|TH|TW|VN)[A-Za-z0-9]{13}'  
        
        # 订单编号模式: 通常以日期代码开头(如250313)加上8个字母数字字符，共14位  
        order_pattern = r'\d{6}[A-Za-z0-9]{8}'  
        
        # 查找所有匹配项  
        sls_matches = re.findall(sls_pattern, text)  
        order_matches = re.findall(order_pattern, text)  
        
        # 更新统计信息  
        self.stats_var.set(f"SLS单号: {len(sls_matches)} | 订单编号: {len(order_matches)}")  
        
        # 根据用户选择返回不同结果  
        order_type = self.order_type.get()  
        output_format = self.output_format.get()  
        
        if order_type == "sls":  
            return {"sls": sls_matches, "order": []}  
        elif order_type == "order":  
            return {"sls": [], "order": order_matches}  
        else:  # both  
            return {"sls": sls_matches, "order": order_matches}  
    
    def format_organization(self):  
        """格式整理功能：按excel格式竖排列整理"""  
        input_text = self.input_text.get("1.0", tk.END)  
        order_data = self.extract_order_numbers(input_text)  
        
        sls_numbers = order_data["sls"]  
        order_numbers = order_data["order"]  
        
        output_format = self.output_format.get()  
        order_type = self.order_type.get()  
        
        if output_format == "single" or order_type != "both":  
            # 单列输出或只处理一种类型时，直接合并列表  
            if order_type == "sls":  
                all_numbers = sls_numbers  
            elif order_type == "order":  
                all_numbers = order_numbers  
            else:  # both  
                all_numbers = sls_numbers + order_numbers  
                
            result = "\n".join(all_numbers)  
            count = len(all_numbers)  
        else:  
            # 双列输出模式 (A/B列)  
            # 将SLS单号放在A列，订单编号放在B列  
            max_rows = max(len(sls_numbers), len(order_numbers))  
            result_rows = []  
            
            for i in range(max_rows):  
                sls_value = sls_numbers[i] if i < len(sls_numbers) else ""  
                order_value = order_numbers[i] if i < len(order_numbers) else ""  
                result_rows.append(f"{sls_value}\t{order_value}")  
                
            result = "\n".join(result_rows)  
            count = len(sls_numbers) + len(order_numbers)  
        
        self.output_text.delete("1.0", tk.END)  
        self.output_text.insert("1.0", result)  
        self.status_var.set(f"已整理 {count} 个订单号")  
    
    def batch_query_format(self):  
        """批量查订单格式：每个订单号后添加逗号，最后一个除外"""  
        input_text = self.input_text.get("1.0", tk.END)  
        order_data = self.extract_order_numbers(input_text)  
        
        sls_numbers = order_data["sls"]  
        order_numbers = order_data["order"]  
        
        output_format = self.output_format.get()  
        order_type = self.order_type.get()  
        
        if output_format == "single" or order_type != "both":  
            # 单列输出或只处理一种类型时  
            if order_type == "sls":  
                all_numbers = sls_numbers  
            elif order_type == "order":  
                all_numbers = order_numbers  
            else:  # both  
                all_numbers = sls_numbers + order_numbers  
                
            if all_numbers:  
                # 除最后一个外，所有订单号后添加逗号  
                formatted_numbers = [num + "," for num in all_numbers[:-1]]  
                formatted_numbers.append(all_numbers[-1])  # 添加最后一个（不带逗号）  
                result = "".join(formatted_numbers)  
                count = len(all_numbers)  
            else:  
                result = ""  
                count = 0  
        else:  
            # 双列输出处理 - 分别处理SLS单号和订单编号  
            sls_formatted = ""  
            order_formatted = ""  
            
            if sls_numbers:  
                sls_temp = [num + "," for num in sls_numbers[:-1]]  
                sls_temp.append(sls_numbers[-1])  
                sls_formatted = "".join(sls_temp)  
                
            if order_numbers:  
                order_temp = [num + "," for num in order_numbers[:-1]]  
                order_temp.append(order_numbers[-1])  
                order_formatted = "".join(order_temp)  
                
            result = f"SLS单号:\n{sls_formatted}\n\n订单编号:\n{order_formatted}"  
            count = len(sls_numbers) + len(order_numbers)  
        
        self.output_text.delete("1.0", tk.END)  
        self.output_text.insert("1.0", result)  
        self.status_var.set(f"已处理 {count} 个订单号为批量查询格式")  
    
    def batch_data_format(self):  
        """批量跑数据格式：'订单号',格式"""  
        input_text = self.input_text.get("1.0", tk.END)  
        order_data = self.extract_order_numbers(input_text)  
        
        sls_numbers = order_data["sls"]  
        order_numbers = order_data["order"]  
        
        output_format = self.output_format.get()  
        order_type = self.order_type.get()  
        
        if output_format == "single" or order_type != "both":  
            # 单列输出或只处理一种类型时  
            if order_type == "sls":  
                all_numbers = sls_numbers  
            elif order_type == "order":  
                all_numbers = order_numbers  
            else:  # both  
                all_numbers = sls_numbers + order_numbers  
                
            if all_numbers:  
                # 除最后一个外，所有订单号格式化为'订单号',  
                formatted_numbers = [f"'{num}'," for num in all_numbers[:-1]]  
                # 最后一个不加逗号  
                formatted_numbers.append(f"'{all_numbers[-1]}'")  
                result = "".join(formatted_numbers)  
                count = len(all_numbers)  
            else:  
                result = ""  
                count = 0  
        else:  
            # 双列输出处理 - 分别处理SLS单号和订单编号  
            sls_formatted = ""  
            order_formatted = ""  
            
            if sls_numbers:  
                sls_temp = [f"'{num}'," for num in sls_numbers[:-1]]  
                sls_temp.append(f"'{sls_numbers[-1]}'")  
                sls_formatted = "".join(sls_temp)  
                
            if order_numbers:  
                order_temp = [f"'{num}'," for num in order_numbers[:-1]]  
                order_temp.append(f"'{order_numbers[-1]}'")  
                order_formatted = "".join(order_temp)  
                
            result = f"SLS单号:\n{sls_formatted}\n\n订单编号:\n{order_formatted}"  
            count = len(sls_numbers) + len(order_numbers)  
        
        self.output_text.delete("1.0", tk.END)  
        self.output_text.insert("1.0", result)  
        self.status_var.set(f"已处理 {count} 个订单号为批量数据格式")  
    
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
        self.stats_var.set("SLS单号: 0 | 订单编号: 0")  

def main():  
    root = tk.Tk()  
    app = OrderProcessorApp(root)  
    root.mainloop()  

if __name__ == "__main__":  
    main()