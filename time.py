import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import pystray
from PIL import Image, ImageDraw
import os
import sys
import tempfile
import json

# 取消单例模式，允许多实例运行
def singleton():
    """允许多实例运行"""
    return True

# 自定义消息框函数，确保在屏幕居中显示
def show_center_messagebox(title, message, icon='warning'):
    """显示居中的消息框"""
    # 创建自定义消息框窗口
    msg_window = tk.Toplevel()
    msg_window.title(title)
    msg_window.resizable(False, False)
    msg_window.transient()  # 设置为临时窗口
    msg_window.grab_set()  # 模态窗口
    
    # 固定窗口大小，确保完整显示所有内容
    window_width = 400
    window_height = 180
    
    # 计算屏幕中心位置
    screen_width = msg_window.winfo_screenwidth()
    screen_height = msg_window.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    msg_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # 设置窗口样式
    msg_window.configure(bg="#ffffff")
    
    # 消息文本
    message_label = ttk.Label(msg_window, text=message, wraplength=window_width-40, justify=tk.CENTER, font= ("Microsoft YaHei", 11))
    message_label.pack(pady=(20, 20), padx=20, fill=tk.BOTH, expand=True)
    
    # 确定按钮
    def on_ok():
        msg_window.destroy()
    
    # 创建按钮
    ok_button = ttk.Button(msg_window, text="确定", command=on_ok, width=10)
    ok_button.pack(pady=(0, 20))
    
    # 等待窗口关闭
    msg_window.wait_window()

class CountdownApp:
    def __init__(self, root):
        self.root = root
        # 先隐藏窗口，避免启动时闪烁
        self.root.withdraw()
        
        self.root.title("多任务倒计时工具")
        # 设置窗口图标
        import os
        import sys
        # 获取当前脚本所在目录
        if getattr(sys, 'frozen', False):
            # 打包后的环境
            if hasattr(sys, '_MEIPASS'):
                # 使用 PyInstaller 的临时目录
                script_dir = sys._MEIPASS
            else:
                # 回退到可执行文件目录
                script_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境
            script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, 'favicon.ico')
        try:
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass  # 如果图标文件不存在或设置失败，忽略错误
        # 基础窗口尺寸
        self.root.geometry("920x550")
        # 设置窗口居中
        self.center_window(920, 550)
        
        # 完成所有设置后显示窗口
        self.root.deiconify()
        
        # 固定窗口大小，不可调整
        self.root.resizable(False, False)
        self.root.configure(bg="#ffffff")

        # ===== 自定义样式 =====
        self.style = ttk.Style(self.root)
        # 设置主题（基础主题）
        self.style.theme_use("clam")
        # 自定义字体 - 统一白底黑字加粗
        self.style.configure(".", font=("Microsoft YaHei", 10, "bold"), foreground="#000000", background="#ffffff")
        # 按钮样式
        self.style.configure("TButton", 
                            font=("Microsoft YaHei", 10, "bold"),
                            background="#22c55e",
                            foreground="white",
                            padding=6)
        self.style.map("TButton",
                       background=[("active", "#16a34a")])
        # 复制按钮样式
        self.style.configure("Copy.TButton", 
                            font=("Microsoft YaHei", 10, "bold"),
                            background="#f59e0b",
                            foreground="white",
                            padding=6)
        self.style.map("Copy.TButton",
                       background=[("active", "#d97706")])
        # 标签样式
        self.style.configure("Title.TLabel", 
                             font=("Microsoft YaHei", 12, "bold"),
                             foreground="#000000",
                             background="#ffffff")
        self.style.configure("Task.TLabel", 
                             font=("Microsoft YaHei", 10, "bold"),
                             foreground="#000000",
                             background="#ffffff")
        self.style.configure("Warning.TLabel",
                             font=("Microsoft YaHei", 10, "bold"),
                             foreground="#dc2626",
                             background="#ffffff")
        # 倒计时任务样式（蓝色背景，加粗字体，蓝色边框）
        self.style.configure("Countdown.TFrame",
                             background="#e6f0ff",
                             bordercolor="#3b82f6",
                             relief="solid",
                             borderwidth=2)
        self.style.configure("Countdown.TLabel",
                             font=("Microsoft YaHei", 10, "bold"),
                             foreground="#000000",
                             background="#e6f0ff")
        # 定时提醒任务样式（绿色背景，加粗字体，绿色边框）
        self.style.configure("Reminder.TFrame",
                             background="#dcfce7",
                             bordercolor="#22c55e",
                             relief="solid",
                             borderwidth=2)
        self.style.configure("Reminder.TLabel",
                             font=("Microsoft YaHei", 10, "bold"),
                             foreground="#000000",
                             background="#dcfce7")
        # 列表框架样式
        self.style.configure("List.TFrame",
                             background="#ffffff")
        # 标签框架样式
        self.style.configure("Title.TFrame",
                             background="#ffffff",
                             bordercolor="#000000",
                             relief="ridge",
                             borderwidth=6)
        # 输入框样式
        self.style.configure("TEntry",
                             fieldbackground="#ffffff",
                             foreground="#000000",
                             bordercolor="#000000",
                             relief="ridge",
                             borderwidth=2)
        # 下拉框样式
        self.style.configure("TCombobox",
                             fieldbackground="#ffffff",
                             foreground="#000000",
                             bordercolor="#000000",
                             relief="ridge",
                             borderwidth=2)
        
        # 存储倒计时任务
        self.countdown_tasks = []
        # 存储提醒任务
        self.reminder_tasks = []
        # 存储当前显示的提醒窗口
        self.alert_windows = []
        # 托盘图标
        self.tray_icon = None
        # 任务更新线程控制
        self.running = True
        # 绑定窗口最小化事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        # 绑定窗口最小化事件
        self.root.bind("<Unmap>", self.on_minimize)
        # 延迟初始化托盘图标
        self.root.after(100, self.init_tray_icon)
        # 启动任务更新线程
        import threading
        self.update_thread = threading.Thread(target=self.update_tasks, daemon=True)
        self.update_thread.start()

        # ===== 界面布局 =====
        # 1. 标题区域
        title_frame = ttk.Frame(root, style="Title.TFrame")
        title_frame.pack(fill=tk.X, padx=20, pady=0)
        title_label = ttk.Label(title_frame, text="多任务倒计时工具", style="Title.TLabel")
        title_label.pack(anchor=tk.CENTER, pady=20)

        # 2. 输入区域（带边框）
        input_frame = ttk.LabelFrame(root, text="倒计提醒", padding="10", style="Title.TFrame")
        input_frame.pack(fill=tk.X, padx=20, pady=0)

        # 输入网格布局
        ttk.Label(input_frame, text="任务名称：", style="Task.TLabel").grid(row=0, column=0, padx=5, pady=4, sticky=tk.E)
        self.name_entry = ttk.Entry(input_frame, width=15)
        self.name_entry.grid(row=0, column=1, padx=5, pady=4)
        self.name_entry.insert(0, "我的倒计提醒")  # 默认名称
        self.name_entry.config(font= ("Microsoft YaHei", 10))
        # 绑定点击事件，清除默认文本
        self.name_entry.bind("<FocusIn>", self.clear_default_text)
        # 绑定回车键触发添加任务
        self.name_entry.bind("<Return>", lambda e: self.add_countdown())

        # 时间输入组
        time_frame = ttk.Frame(input_frame)
        time_frame.grid(row=0, column=2, padx=10, pady=4, columnspan=1)
        ttk.Label(time_frame, text="时长：", style="Task.TLabel").grid(row=0, column=0, padx=5)
        self.hour_entry = ttk.Entry(time_frame, width=6)
        self.hour_entry.grid(row=0, column=1, padx=2)
        self.hour_entry.insert(0, "0")
        # 绑定回车键触发添加任务
        self.hour_entry.bind("<Return>", lambda e: self.add_countdown())
        # 绑定点击事件，清除默认值
        self.hour_entry.bind("<FocusIn>", self.clear_hour_default)
        ttk.Label(time_frame, text="时", style="Task.TLabel").grid(row=0, column=2, padx=2)

        self.minute_entry = ttk.Entry(time_frame, width=6)
        self.minute_entry.grid(row=0, column=3, padx=2)
        self.minute_entry.insert(0, "0")
        # 绑定回车键触发添加任务
        self.minute_entry.bind("<Return>", lambda e: self.add_countdown())
        # 绑定点击事件，清除默认值
        self.minute_entry.bind("<FocusIn>", self.clear_minute_default)
        ttk.Label(time_frame, text="分", style="Task.TLabel").grid(row=0, column=4, padx=2)

        self.second_entry = ttk.Entry(time_frame, width=6)
        self.second_entry.grid(row=0, column=5, padx=2)
        self.second_entry.insert(0, "10")
        # 绑定回车键触发添加任务
        self.second_entry.bind("<Return>", lambda e: self.add_countdown())
        # 绑定点击事件，清除默认值
        self.second_entry.bind("<FocusIn>", self.clear_second_default)
        ttk.Label(time_frame, text="秒                                           ", style="Task.TLabel").grid(row=0, column=6, padx=2)

        # 新增按钮（使用默认TButton样式，确保可见）
        add_btn = ttk.Button(input_frame, text="添加任务", command=self.add_countdown)
        add_btn.grid(row=0, column=3, padx=30, pady=4)

        # 3. 定时提醒区域
        reminder_frame = ttk.LabelFrame(root, text="定时提醒", padding="10", style="Title.TFrame")
        reminder_frame.pack(fill=tk.X, padx=20, pady=0)

        # 定时提醒输入 - 调整布局以适应1050宽度
        ttk.Label(reminder_frame, text="提醒名称：", style="Task.TLabel").grid(row=0, column=0, padx=5, pady=4, sticky=tk.E)
        self.reminder_name_entry = ttk.Entry(reminder_frame, width=15)
        self.reminder_name_entry.grid(row=0, column=1, padx=5, pady=4)
        self.reminder_name_entry.insert(0, "我的定时提醒")  # 默认名称
        self.reminder_name_entry.config(font= ("Microsoft YaHei", 10))
        # 绑定点击事件，清除默认文本
        self.reminder_name_entry.bind("<FocusIn>", self.clear_reminder_default_text)
        # 绑定回车键触发添加提醒
        self.reminder_name_entry.bind("<Return>", lambda e: self.add_reminder())

        # 日期时间选择
        ttk.Label(reminder_frame, text="提醒时间：", style="Task.TLabel").grid(row=0, column=2, padx=5, pady=4, sticky=tk.E)
        
        # 获取当前北京时间，并加上30秒
        import datetime
        now = datetime.datetime.now()
        reminder_time = now + datetime.timedelta(seconds=30)
        
        # 日期时间选择合并为一行
        datetime_frame = ttk.Frame(reminder_frame)
        datetime_frame.grid(row=0, column=2, padx=5, pady=4, columnspan=1, sticky=tk.W)
        
        # 日期部分
        ttk.Label(datetime_frame, text="日期：", style="Task.TLabel").pack(side=tk.LEFT, padx=1)
        self.reminder_year = ttk.Combobox(datetime_frame, width=5, values=[str(reminder_time.year), str(reminder_time.year+1)])
        self.reminder_year.pack(side=tk.LEFT, padx=1)
        self.reminder_year.set(str(reminder_time.year))
        # 绑定回车键触发添加提醒
        self.reminder_year.bind("<Return>", lambda e: self.add_reminder())
        
        ttk.Label(datetime_frame, text="年", style="Task.TLabel").pack(side=tk.LEFT, padx=0)
        self.reminder_month = ttk.Combobox(datetime_frame, width=3, values=[f"{i:02d}" for i in range(1, 13)])
        self.reminder_month.pack(side=tk.LEFT, padx=1)
        self.reminder_month.set(f"{reminder_time.month:02d}")
        # 绑定回车键触发添加提醒
        self.reminder_month.bind("<Return>", lambda e: self.add_reminder())
        
        ttk.Label(datetime_frame, text="月", style="Task.TLabel").pack(side=tk.LEFT, padx=0)
        self.reminder_day = ttk.Combobox(datetime_frame, width=3, values=[f"{i:02d}" for i in range(1, 32)])
        self.reminder_day.pack(side=tk.LEFT, padx=1)
        self.reminder_day.set(f"{reminder_time.day:02d}")
        # 绑定回车键触发添加提醒
        self.reminder_day.bind("<Return>", lambda e: self.add_reminder())
        ttk.Label(datetime_frame, text="日", style="Task.TLabel").pack(side=tk.LEFT, padx=5)
        
        # 时间部分
        ttk.Label(datetime_frame, text="时间：", style="Task.TLabel").pack(side=tk.LEFT, padx=1)
        self.reminder_hour = ttk.Combobox(datetime_frame, width=3, values=[f"{i:02d}" for i in range(24)])
        self.reminder_hour.pack(side=tk.LEFT, padx=1)
        self.reminder_hour.set(f"{reminder_time.hour:02d}")
        # 绑定回车键触发添加提醒
        self.reminder_hour.bind("<Return>", lambda e: self.add_reminder())
        ttk.Label(datetime_frame, text="时", style="Task.TLabel").pack(side=tk.LEFT, padx=0)
        
        self.reminder_minute = ttk.Combobox(datetime_frame, width=3, values=[f"{i:02d}" for i in range(60)])
        self.reminder_minute.pack(side=tk.LEFT, padx=1)
        self.reminder_minute.set(f"{reminder_time.minute:02d}")
        # 绑定回车键触发添加提醒
        self.reminder_minute.bind("<Return>", lambda e: self.add_reminder())
        ttk.Label(datetime_frame, text="分", style="Task.TLabel").pack(side=tk.LEFT, padx=1)
        
        # 新增秒选择
        self.reminder_second = ttk.Combobox(datetime_frame, width=3, values=[f"{i:02d}" for i in range(60)])
        self.reminder_second.pack(side=tk.LEFT, padx=1)
        self.reminder_second.set(f"{reminder_time.second:02d}")
        # 绑定回车键触发添加提醒
        self.reminder_second.bind("<Return>", lambda e: self.add_reminder())
        ttk.Label(datetime_frame, text="秒", style="Task.TLabel").pack(side=tk.LEFT, padx=1)
        
        # 添加提醒按钮 - 与添加任务按钮对齐
        add_reminder_btn = ttk.Button(reminder_frame, text="添加提醒", command=self.add_reminder)
        add_reminder_btn.grid(row=0, column=3, padx=10, pady=4)

        # 4. 主内容区域（左右布局）
        main_content_frame = ttk.Frame(root, style="List.TFrame")
        main_content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))  # 保持左右内边距
        
        # 固定主内容区域宽度为880px（920-20*2）
        main_content_frame.update_idletasks()
        main_content_frame.config(width=880)
        
        # 当前任务列表，占据整个主内容区域
        left_frame = ttk.LabelFrame(main_content_frame, text="当前任务列表", padding="15", style="Title.TFrame")
        left_frame.place(x=0, y=0, width=880, relheight=1)  # 宽度880，占据整个主内容区域
        

        


        # 任务容器（带滚动条）
        self.task_canvas = tk.Canvas(left_frame, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.task_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.task_canvas, style="List.TFrame")

        # 创建窗口并保存引用
        scrollable_window = self.task_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # 绑定scrollable_frame的配置事件
        def on_frame_configure(event):
            try:
                if not self.task_canvas.winfo_exists():
                    return
                self.task_canvas.configure(scrollregion=self.task_canvas.bbox("all"))
                # 检查是否需要显示滚动条
                if self.task_canvas.winfo_height() > 0:  # 确保canvas已经初始化
                    if self.task_canvas.bbox("all")[3] > self.task_canvas.winfo_height():
                        if not scrollbar.winfo_ismapped():
                            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                            # 调整scrollable_window的宽度
                            self.task_canvas.itemconfig(scrollable_window, width=self.task_canvas.winfo_width() - scrollbar.winfo_width())
                    else:
                        if scrollbar.winfo_ismapped():
                            scrollbar.pack_forget()
                            # 调整scrollable_window的宽度
                            self.task_canvas.itemconfig(scrollable_window, width=self.task_canvas.winfo_width())
            except Exception as e:
                print(f"配置框架失败: {e}")
        
        self.scrollable_frame.bind("<Configure>", on_frame_configure)
        
        # 绑定canvas的配置事件，让scrollable_frame宽度随canvas调整
        def on_canvas_configure(event):
            try:
                if not self.task_canvas.winfo_exists():
                    return
                # 确保scrollable_frame宽度与canvas一致，减去滚动条的宽度
                if scrollbar.winfo_ismapped():
                    scrollbar_width = scrollbar.winfo_width()
                    self.task_canvas.itemconfig(scrollable_window, width=event.width - scrollbar_width)
                else:
                    self.task_canvas.itemconfig(scrollable_window, width=event.width)
            except Exception as e:
                print(f"配置画布失败: {e}")
        
        self.task_canvas.bind("<Configure>", on_canvas_configure)
        
        self.task_canvas.configure(yscrollcommand=scrollbar.set)

        self.task_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 加载任务存档
        self.load_tasks()
        

        

        




    def center_window(self, width, height):
        """将窗口居中显示"""
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # 计算居中坐标
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        # 设置窗口位置
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def clear_default_text(self, event):
        """点击任务名称输入框时清除默认文本"""
        if self.name_entry.get() == "我的倒计提醒":
            self.name_entry.delete(0, tk.END)
    
    def clear_reminder_default_text(self, event):
        """点击提醒名称输入框时清除默认文本"""
        if self.reminder_name_entry.get() == "我的定时提醒":
            self.reminder_name_entry.delete(0, tk.END)
    
    def clear_hour_default(self, event):
        """点击小时输入框时清除默认值"""
        if self.hour_entry.get() == "0":
            self.hour_entry.delete(0, tk.END)
    
    def clear_minute_default(self, event):
        """点击分钟输入框时清除默认值"""
        if self.minute_entry.get() == "0":
            self.minute_entry.delete(0, tk.END)
    
    def clear_second_default(self, event):
        """点击秒输入框时清除默认值"""
        if self.second_entry.get() == "10":
            self.second_entry.delete(0, tk.END)

    def add_countdown(self):
        """新增倒计时任务"""
        # 检查任务数量限制
        total_tasks = len(self.countdown_tasks) + len(self.reminder_tasks)
        if total_tasks >= 10:
            show_center_messagebox("任务数量限制", "当前任务列表最多只能添加10条任务，请先删除部分任务后再添加！")
            return
            
        # 1. 输入验证
        name = self.name_entry.get().strip()
        if not name:
            show_center_messagebox("输入提示", "任务名称不能为空！")
            return

        try:
            # 当时分秒为空时，默认按0处理
            hour_str = self.hour_entry.get().strip()
            minute_str = self.minute_entry.get().strip()
            second_str = self.second_entry.get().strip()
            
            hour = int(hour_str) if hour_str else 0
            minute = int(minute_str) if minute_str else 0
            second = int(second_str) if second_str else 0
            
            total_seconds = hour * 3600 + minute * 60 + second
            if total_seconds <= 0:
                show_center_messagebox("输入提示", "总时长必须大于0秒！")
                return
        except ValueError:
            show_center_messagebox("输入提示", "时/分/秒必须输入有效数字！")
            return

        # 2. 创建任务行（带边框）
        task_row = ttk.Frame(self.scrollable_frame, style="Countdown.TFrame")
        task_row.pack(fill=tk.X, pady=0, ipady=8, padx=0)

        # 创建内部框架来控制布局
        inner_frame = ttk.Frame(task_row, style="Countdown.TFrame")
        inner_frame.pack(fill=tk.X, expand=True, padx=5)
        
        # 配置三列布局，使用固定宽度
        inner_frame.columnconfigure(0, minsize=400)  # 任务名称固定宽度
        inner_frame.columnconfigure(1, minsize=150)  # 时间固定宽度
        inner_frame.columnconfigure(2, minsize=200)  # 按钮区固定宽度
        inner_frame.rowconfigure(0, weight=1)  # 行占满高度

        # 任务名称 - 添加[倒计提醒]前缀
        name_label = ttk.Label(inner_frame, text=f"[倒计提醒] {name}", style="Countdown.TLabel", anchor=tk.W, width=30)
        name_label.grid(row=0, column=0, sticky="w", padx=5)

        # 剩余时间 - 与表头对齐（居中）
        remaining_label = ttk.Label(inner_frame, text=self.format_time(total_seconds), style="Countdown.TLabel", anchor=tk.CENTER, width=10)
        remaining_label.grid(row=0, column=1, sticky="we", padx=5)

        # 3. 存储任务信息
        import datetime
        import time
        target_time = datetime.datetime.now() + datetime.timedelta(seconds=total_seconds)
        start_time = time.time()  # 记录任务开始时间
        task_info = {
            "name": name,
            "total_seconds": total_seconds,
            "remaining_seconds": total_seconds,
            "target_time": target_time,
            "start_time": start_time,
            "thread": None,
            "label": remaining_label,
            "row": task_row,
            "running": True
        }
        self.countdown_tasks.append(task_info)

        # 按钮区框架
        button_frame = ttk.Frame(inner_frame, style="Countdown.TFrame")
        button_frame.grid(row=0, column=2, sticky="we", padx=5)
        
        # 删除按钮
        delete_btn = ttk.Button(button_frame, text="删除", command=lambda r=task_row, info=task_info: self.delete_countdown(r, info), width=10)
        delete_btn.pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # 复制按钮
        copy_btn = ttk.Button(button_frame, text="复制", command=lambda info=task_info: self.copy_task(info), width=10, style="Copy.TButton")
        copy_btn.pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # 任务将由 update_tasks 方法统一处理

        # 清空输入框（恢复默认名称）
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, "我的倒计提醒")
        self.hour_entry.delete(0, tk.END)
        self.hour_entry.insert(0, "0")
        self.minute_entry.delete(0, tk.END)
        self.minute_entry.insert(0, "0")
        self.second_entry.delete(0, tk.END)
        self.second_entry.insert(0, "10")

    def update_tasks(self):
        """统一更新所有任务的状态（在独立线程中运行）"""
        import time
        # 收集需要更新的UI操作
        ui_updates = []
        
        while self.running:
            try:
                current_time = time.time()
                ui_updates.clear()
                
                # 处理倒计时任务
                for task_info in self.countdown_tasks:
                    if task_info["running"] and task_info["remaining_seconds"] > 0:
                        # 使用基于系统时间的精确计算
                        if "start_time" in task_info:
                            # 计算已经过去的时间
                            elapsed = current_time - task_info["start_time"]
                            # 重新计算剩余时间
                            task_info["remaining_seconds"] = max(0, task_info["total_seconds"] - elapsed)
                        else:
                            # 初始化开始时间
                            task_info["start_time"] = current_time
                        
                        if task_info["remaining_seconds"] <= 0:
                            task_info["remaining_seconds"] = 0
                            # 任务完成，显示提醒
                            # 在主线程中显示提醒
                            self.root.after(0, lambda name=task_info["name"]: self.show_alert(name, task_type="countdown", task_info=task_info))
                    # 无论窗口是否隐藏，都更新时间标签（如果标签存在）
                    if "label" in task_info and task_info["label"] and task_info["running"]:
                        # 检查是否需要更新UI
                        need_update = False
                        if "last_update" in task_info:
                            if current_time - task_info["last_update"] >= 0.1:  # 每0.1秒更新一次UI
                                need_update = True
                                task_info["last_update"] = current_time
                        else:
                            need_update = True
                            task_info["last_update"] = current_time
                        
                        if need_update:
                            # 收集UI更新操作
                            def create_update_func(task_info):
                                def update_func():
                                    try:
                                        if task_info["remaining_seconds"] <= 0:
                                            task_info["label"].config(text="✅ 时间到！", foreground="#dc2626")
                                        else:
                                            task_info["label"].config(text=self.format_time(task_info["remaining_seconds"]))
                                    except tk.TclError:
                                        # 标签已被销毁，忽略错误
                                        pass
                                return update_func
                            ui_updates.append(create_update_func(task_info))
                
                # 处理提醒任务
                for reminder_info in self.reminder_tasks:
                    if reminder_info["running"] and reminder_info["remaining_seconds"] > 0:
                        # 使用基于系统时间的精确计算
                        if "target_time" in reminder_info:
                            # 计算剩余时间
                            import datetime
                            current_datetime = datetime.datetime.now()
                            remaining = (reminder_info["target_time"] - current_datetime).total_seconds()
                            reminder_info["remaining_seconds"] = max(0, remaining)
                        
                        if reminder_info["remaining_seconds"] <= 0:
                            reminder_info["remaining_seconds"] = 0
                            # 任务完成，显示提醒
                            # 在主线程中显示提醒
                            self.root.after(0, lambda name=reminder_info["name"]: self.show_alert(name, task_type="reminder", task_info=reminder_info))
                    # 无论窗口是否隐藏，都更新时间标签（如果标签存在）
                    if "label" in reminder_info and reminder_info["label"] and reminder_info["running"]:
                        # 检查是否需要更新UI
                        need_update = False
                        if "last_update" in reminder_info:
                            if current_time - reminder_info["last_update"] >= 0.1:  # 每0.1秒更新一次UI
                                need_update = True
                                reminder_info["last_update"] = current_time
                        else:
                            need_update = True
                            reminder_info["last_update"] = current_time
                        
                        if need_update:
                            # 收集UI更新操作
                            def create_update_func(reminder_info):
                                def update_func():
                                    try:
                                        if reminder_info["remaining_seconds"] <= 0:
                                            reminder_info["label"].config(text="✅ 时间到！", foreground="#dc2626")
                                        else:
                                            reminder_info["label"].config(text=self.format_time(reminder_info["remaining_seconds"]))
                                    except tk.TclError:
                                        # 标签已被销毁，忽略错误
                                        pass
                                return update_func
                            ui_updates.append(create_update_func(reminder_info))
                
                # 批量执行UI更新
                if ui_updates:
                    def batch_update():
                        for update_func in ui_updates:
                            update_func()
                    self.root.after(0, batch_update)
            except Exception as e:
                print(f"更新任务失败: {e}")
            finally:
                # 短暂休眠，避免CPU占用过高
                time.sleep(0.1)
    
    def delete_reminder(self, task_row, reminder_info):
        """删除提醒任务"""
        # 停止任务线程
        reminder_info["running"] = False
        # 销毁任务行
        task_row.destroy()
        # 从任务列表中移除
        if reminder_info in self.reminder_tasks:
            self.reminder_tasks.remove(reminder_info)
        # 更新滚动区域
        self.update_scrollable_frame()
        # 弹出复制任务对话框
        self.copy_reminder(reminder_info)
    
    def copy_reminder(self, reminder_info):
        """复制定时提醒任务"""
        # 创建复制对话框
        copy_window = tk.Toplevel(self.root)
        copy_window.title("复制定时提醒")
        copy_window.resizable(False, False)
        copy_window.transient(self.root)
        copy_window.grab_set()
        
        # 设置窗口大小和位置
        window_width = 500
        window_height = 250
        screen_width = copy_window.winfo_screenwidth()
        screen_height = copy_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        copy_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        copy_window.configure(bg="#ffffff")
        
        # 创建内容框架
        content_frame = ttk.Frame(copy_window, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置列权重，使内容居中
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=0)
        content_frame.columnconfigure(2, weight=1)
        
        # 任务名称输入 - 居中显示
        ttk.Label(content_frame, text="提醒名称：", style="Task.TLabel").grid(row=0, column=0, padx=5, pady=10, sticky=tk.E)
        name_var = tk.StringVar(value=reminder_info["name"])
        name_entry = ttk.Entry(content_frame, textvariable=name_var, width=20)
        name_entry.grid(row=0, column=1, padx=5, pady=10, sticky=tk.W)
        ttk.Label(content_frame, text="", style="Task.TLabel").grid(row=0, column=2, padx=5, pady=10)
        
        # 时间选择 - 居中显示
        ttk.Label(content_frame, text="提醒时间：", style="Task.TLabel").grid(row=1, column=0, padx=5, pady=10, sticky=tk.E)
        
        # 时间选择框架
        time_frame = ttk.Frame(content_frame)
        time_frame.grid(row=1, column=1, padx=5, pady=10, sticky=tk.W)
        
        # 获取当前时间
        import datetime
        if "target_time" in reminder_info:
            target_time = reminder_info["target_time"]
        else:
            target_time = datetime.datetime.now() + datetime.timedelta(seconds=30)
        
        # 时间部分（只显示时分秒）
        hour_var = tk.StringVar(value=f"{target_time.hour:02d}")
        hour_entry = ttk.Combobox(time_frame, textvariable=hour_var, width=3, values=[f"{i:02d}" for i in range(24)])
        hour_entry.pack(side=tk.LEFT, padx=1)
        ttk.Label(time_frame, text="时", style="Task.TLabel").pack(side=tk.LEFT, padx=0)
        
        minute_var = tk.StringVar(value=f"{target_time.minute:02d}")
        minute_entry = ttk.Combobox(time_frame, textvariable=minute_var, width=3, values=[f"{i:02d}" for i in range(60)])
        minute_entry.pack(side=tk.LEFT, padx=1)
        ttk.Label(time_frame, text="分", style="Task.TLabel").pack(side=tk.LEFT, padx=1)
        
        second_var = tk.StringVar(value=f"{target_time.second:02d}")
        second_entry = ttk.Combobox(time_frame, textvariable=second_var, width=3, values=[f"{i:02d}" for i in range(60)])
        second_entry.pack(side=tk.LEFT, padx=1)
        ttk.Label(time_frame, text="秒", style="Task.TLabel").pack(side=tk.LEFT, padx=1)
        
        # 清除默认值函数
        def clear_name_default(event):
            if name_entry.get() == reminder_info["name"]:
                name_entry.delete(0, tk.END)
        
        def clear_hour_default(event):
            if hour_entry.get() == f"{target_time.hour:02d}":
                hour_entry.delete(0, tk.END)
        
        def clear_minute_default(event):
            if minute_entry.get() == f"{target_time.minute:02d}":
                minute_entry.delete(0, tk.END)
        
        def clear_second_default(event):
            if second_entry.get() == f"{target_time.second:02d}":
                second_entry.delete(0, tk.END)
        
        # 绑定回车键触发确定按钮功能
        name_entry.bind("<Return>", lambda e: on_ok())
        hour_entry.bind("<Return>", lambda e: on_ok())
        minute_entry.bind("<Return>", lambda e: on_ok())
        second_entry.bind("<Return>", lambda e: on_ok())
        
        # 绑定点击事件，清除默认值
        name_entry.bind("<FocusIn>", clear_name_default)
        hour_entry.bind("<FocusIn>", clear_hour_default)
        minute_entry.bind("<FocusIn>", clear_minute_default)
        second_entry.bind("<FocusIn>", clear_second_default)
        
        ttk.Label(content_frame, text="", style="Task.TLabel").grid(row=1, column=2, padx=5, pady=10)
        
        # 按钮框架 - 居中显示
        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        # 确定按钮
        def on_ok():
            # 检查任务数量限制
            total_tasks = len(self.countdown_tasks) + len(self.reminder_tasks)
            if total_tasks >= 10:
                show_center_messagebox("任务数量限制", "当前任务列表最多只能添加10条任务，请先删除部分任务后再添加！")
                copy_window.destroy()
                return
            
            # 验证输入
            task_name = name_var.get().strip()
            if not task_name:
                show_center_messagebox("输入提示", "提醒名称不能为空！")
                return
            
            try:
                # 获取当前日期
                current_date = datetime.datetime.now()
                year = current_date.year
                month = current_date.month
                day = current_date.day
                
                # 获取选择的时间，当时分秒为空时默认按0处理
                hour_str = hour_var.get().strip()
                minute_str = minute_var.get().strip()
                second_str = second_var.get().strip()
                
                hour = int(hour_str) if hour_str else 0
                minute = int(minute_str) if minute_str else 0
                second = int(second_str) if second_str else 0
                
                # 计算目标时间
                target_time = datetime.datetime(year, month, day, hour, minute, second)
                current_time = datetime.datetime.now()
                
                # 计算时间差（秒）
                time_diff = (target_time - current_time).total_seconds()
                
                if time_diff <= 0:
                    show_center_messagebox("输入提示", "提醒时间必须在当前时间之后！")
                    return
                    
            except ValueError:
                show_center_messagebox("输入提示", "请输入有效的日期时间！")
                return
            
            # 创建新的定时提醒任务
            # 2. 创建任务行
            task_row = ttk.Frame(self.scrollable_frame, style="Reminder.TFrame")
            task_row.pack(fill=tk.X, pady=0, ipady=8, padx=0)
            
            # 创建内部框架来控制布局
            inner_frame = ttk.Frame(task_row, style="Reminder.TFrame")
            inner_frame.pack(fill=tk.X, expand=True, padx=5)
            
            # 配置三列布局，使用固定宽度
            inner_frame.columnconfigure(0, minsize=400)  # 任务名称固定宽度
            inner_frame.columnconfigure(1, minsize=150)  # 时间固定宽度
            inner_frame.columnconfigure(2, minsize=200)  # 按钮区固定宽度
            inner_frame.rowconfigure(0, weight=1)  # 行占满高度
            
            # 任务名称（标记为提醒） - 与表头对齐，使用ellipsis处理长文本
            name_label = ttk.Label(inner_frame, text=f"[定时提醒] {task_name}", style="Reminder.TLabel", anchor=tk.W, width=30, )
            name_label.grid(row=0, column=0, sticky="w", padx=5)
            
            # 剩余时间 - 与表头对齐（居中）
            remaining_label = ttk.Label(inner_frame, text=self.format_time(int(time_diff)), style="Reminder.TLabel", anchor=tk.CENTER, width=10)
            remaining_label.grid(row=0, column=1, sticky="we", padx=5)
            
            # 3. 存储任务信息
            new_reminder_info = {
                "name": task_name,
                "target_time": target_time,
                "remaining_seconds": int(time_diff),
                "thread": None,
                "label": remaining_label,
                "row": task_row,
                "running": True
            }
            self.reminder_tasks.append(new_reminder_info)
            
            # 按钮区框架
            button_frame = ttk.Frame(inner_frame, style="Reminder.TFrame")
            button_frame.grid(row=0, column=2, sticky="we", padx=5)
            
            # 删除按钮
            delete_btn = ttk.Button(button_frame, text="删除", command=lambda r=task_row, info=new_reminder_info: self.delete_reminder(r, info), width=10)
            delete_btn.pack(side=tk.LEFT, padx=5, fill=tk.Y)
            
            # 复制按钮
            copy_btn = ttk.Button(button_frame, text="复制", command=lambda info=new_reminder_info: self.copy_reminder(info), width=10, style="Copy.TButton")
            copy_btn.pack(side=tk.LEFT, padx=5, fill=tk.Y)
            
            # 任务将由 update_tasks 方法统一处理
            
            # 关闭对话框
            copy_window.destroy()
        
        # 取消按钮
        def on_cancel():
            copy_window.destroy()
        
        # 按钮
        ok_button = ttk.Button(button_frame, text="确定", command=on_ok, width=10)
        ok_button.pack(side=tk.LEFT, padx=10)
        cancel_button = ttk.Button(button_frame, text="取消", command=on_cancel, width=10)
        cancel_button.pack(side=tk.LEFT, padx=10)

    def update_time_label(self, task_info, finished=False):
        """更新剩余时间显示"""
        # 检查任务是否仍在运行，避免更新已删除任务的标签
        if not task_info.get("running"):
            return
        
        try:
            # 根据任务类型选择正确的样式
            task_type = "Countdown"
            if "target_time" in task_info:
                task_type = "Reminder"
            
            if finished:
                # 保持标签的背景色与任务类型一致
                task_info["label"].config(text="✅ 时间到！", foreground="#dc2626")
            else:
                task_info["label"].config(text=self.format_time(task_info["remaining_seconds"]), style=f"{task_type}.TLabel")
        except tk.TclError:
            # 标签已被销毁，忽略错误
            pass

    def format_time(self, seconds):
        """格式化时间为 00:00:00"""
        # 将浮点数转换为整数
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def delete_countdown(self, task_row, task_info):
        """删除倒计时任务"""
        # 停止任务线程
        task_info["running"] = False
        # 销毁任务行
        task_row.destroy()
        # 从任务列表中移除
        if task_info in self.countdown_tasks:
            self.countdown_tasks.remove(task_info)
        # 更新滚动区域
        self.update_scrollable_frame()
        # 弹出复制任务对话框
        self.copy_task(task_info)
    
    def copy_task(self, task_info):
        """复制任务"""
        # 创建复制对话框
        copy_window = tk.Toplevel(self.root)
        copy_window.title("复制任务")
        copy_window.resizable(False, False)
        copy_window.transient(self.root)
        copy_window.grab_set()
        
        # 设置窗口大小和位置
        window_width = 400
        window_height = 200
        screen_width = copy_window.winfo_screenwidth()
        screen_height = copy_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        copy_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        copy_window.configure(bg="#ffffff")
        
        # 创建内容框架
        content_frame = ttk.Frame(copy_window, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置列权重，使内容居中
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=0)
        content_frame.columnconfigure(2, weight=1)
        
        # 任务名称输入 - 居中显示
        ttk.Label(content_frame, text="任务名称：", style="Task.TLabel").grid(row=0, column=0, padx=5, pady=10, sticky=tk.E)
        name_var = tk.StringVar(value=task_info["name"])
        name_entry = ttk.Entry(content_frame, textvariable=name_var, width=20)
        name_entry.grid(row=0, column=1, padx=5, pady=10, sticky=tk.W)
        ttk.Label(content_frame, text="", style="Task.TLabel").grid(row=0, column=2, padx=5, pady=10)
        
        # 倒计时时长输入 - 居中显示
        ttk.Label(content_frame, text="倒计时时长：", style="Task.TLabel").grid(row=1, column=0, padx=5, pady=10, sticky=tk.E)
        
        # 时长输入框架
        time_frame = ttk.Frame(content_frame)
        time_frame.grid(row=1, column=1, padx=5, pady=10, sticky=tk.W)
        
        # 获取当前时长
        duration = task_info["total_seconds"]
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        seconds = duration % 60
        
        # 小时输入
        hour_var = tk.StringVar(value=str(hours))
        hour_entry = ttk.Entry(time_frame, textvariable=hour_var, width=6)
        hour_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(time_frame, text="时", style="Task.TLabel").pack(side=tk.LEFT, padx=2)
        
        # 分钟输入
        minute_var = tk.StringVar(value=str(minutes))
        minute_entry = ttk.Entry(time_frame, textvariable=minute_var, width=6)
        minute_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(time_frame, text="分", style="Task.TLabel").pack(side=tk.LEFT, padx=2)
        
        # 秒输入
        second_var = tk.StringVar(value=str(seconds))
        second_entry = ttk.Entry(time_frame, textvariable=second_var, width=6)
        second_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(time_frame, text="秒", style="Task.TLabel").pack(side=tk.LEFT, padx=2)
        
        # 清除默认值函数
        def clear_name_default(event):
            if name_entry.get() == task_info["name"]:
                name_entry.delete(0, tk.END)
        
        def clear_hour_default(event):
            if hour_entry.get() == str(hours):
                hour_entry.delete(0, tk.END)
        
        def clear_minute_default(event):
            if minute_entry.get() == str(minutes):
                minute_entry.delete(0, tk.END)
        
        def clear_second_default(event):
            if second_entry.get() == str(seconds):
                second_entry.delete(0, tk.END)
        
        # 绑定回车键触发确定按钮功能
        name_entry.bind("<Return>", lambda e: on_ok())
        hour_entry.bind("<Return>", lambda e: on_ok())
        minute_entry.bind("<Return>", lambda e: on_ok())
        second_entry.bind("<Return>", lambda e: on_ok())
        
        # 绑定点击事件，清除默认值
        name_entry.bind("<FocusIn>", clear_name_default)
        hour_entry.bind("<FocusIn>", clear_hour_default)
        minute_entry.bind("<FocusIn>", clear_minute_default)
        second_entry.bind("<FocusIn>", clear_second_default)
        
        ttk.Label(content_frame, text="", style="Task.TLabel").grid(row=1, column=2, padx=5, pady=10)
        
        # 按钮框架 - 居中显示
        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        # 确定按钮
        def on_ok():
            # 检查任务数量限制
            total_tasks = len(self.countdown_tasks) + len(self.reminder_tasks)
            if total_tasks >= 10:
                show_center_messagebox("任务数量限制", "当前任务列表最多只能添加10条任务，请先删除部分任务后再添加！")
                copy_window.destroy()
                return
            
            # 验证输入
            task_name = name_var.get().strip()
            if not task_name:
                show_center_messagebox("输入提示", "任务名称不能为空！")
                return
            
            try:
                # 当时分秒为空时，默认按0处理
                hour_str = hour_var.get().strip()
                minute_str = minute_var.get().strip()
                second_str = second_var.get().strip()
                
                hours = int(hour_str) if hour_str else 0
                minutes = int(minute_str) if minute_str else 0
                seconds = int(second_str) if second_str else 0
                
                total_seconds = hours * 3600 + minutes * 60 + seconds
                if total_seconds <= 0:
                    show_center_messagebox("输入提示", "总时长必须大于0秒！")
                    return
            except ValueError:
                show_center_messagebox("输入提示", "时/分/秒必须输入有效数字！")
                return
            
            # 创建新的倒计时任务
            # 2. 创建任务行（带边框）
            task_row = ttk.Frame(self.scrollable_frame, style="Countdown.TFrame")
            task_row.pack(fill=tk.X, pady=0, ipady=8, padx=0)

            # 创建内部框架来控制布局
            inner_frame = ttk.Frame(task_row, style="Countdown.TFrame")
            inner_frame.pack(fill=tk.X, expand=True, padx=5)
            
            # 配置三列布局，使用固定宽度
            inner_frame.columnconfigure(0, minsize=400)  # 任务名称固定宽度
            inner_frame.columnconfigure(1, minsize=150)  # 时间固定宽度
            inner_frame.columnconfigure(2, minsize=200)  # 按钮区固定宽度
            inner_frame.rowconfigure(0, weight=1)  # 行占满高度

            # 任务名称 - 添加[倒计提醒]前缀，使用ellipsis处理长文本
            name_label = ttk.Label(inner_frame, text=f"[倒计提醒] {task_name}", style="Countdown.TLabel", anchor=tk.W, width=30, )
            name_label.grid(row=0, column=0, sticky="w", padx=5)

            # 剩余时间 - 与表头对齐（居中）
            remaining_label = ttk.Label(inner_frame, text=self.format_time(total_seconds), style="Countdown.TLabel", anchor=tk.CENTER, width=10)
            remaining_label.grid(row=0, column=1, sticky="we", padx=5)

            # 存储任务信息
            import datetime
            import time
            target_time = datetime.datetime.now() + datetime.timedelta(seconds=total_seconds)
            start_time = time.time()  # 记录任务开始时间
            new_task_info = {
                "name": task_name,
                "total_seconds": total_seconds,
                "remaining_seconds": total_seconds,
                "target_time": target_time,
                "start_time": start_time,
                "thread": None,
                "label": remaining_label,
                "row": task_row,
                "running": True
            }
            self.countdown_tasks.append(new_task_info)

            # 按钮区框架
            button_frame = ttk.Frame(inner_frame, style="Countdown.TFrame")
            button_frame.grid(row=0, column=2, sticky="we", padx=5)
            
            # 删除按钮
            delete_btn = ttk.Button(button_frame, text="删除", command=lambda r=task_row, info=new_task_info: self.delete_countdown(r, info), width=10)
            delete_btn.pack(side=tk.LEFT, padx=5, fill=tk.Y)
            
            # 复制按钮
            copy_btn = ttk.Button(button_frame, text="复制", command=lambda info=new_task_info: self.copy_task(info), width=10, style="Copy.TButton")
            copy_btn.pack(side=tk.LEFT, padx=5, fill=tk.Y)

            # 任务将由 update_tasks 方法统一处理
            
            # 关闭对话框
            copy_window.destroy()
        
        # 取消按钮
        def on_cancel():
            copy_window.destroy()
        
        # 按钮
        ok_button = ttk.Button(button_frame, text="确定", command=on_ok, width=10)
        ok_button.pack(side=tk.LEFT, padx=10)
        cancel_button = ttk.Button(button_frame, text="取消", command=on_cancel, width=10)
        cancel_button.pack(side=tk.LEFT, padx=10)
    
    def copy_task_from_alert(self, task_info, task_type):
        """从提醒窗口复制任务"""
        if task_type == "countdown":
            # 复制倒计时任务
            self.copy_task(task_info)
        else:
            # 复制提醒任务
            self.copy_reminder(task_info)
    
    def add_reminder(self):
        """添加定时提醒任务"""
        # 检查任务数量限制
        total_tasks = len(self.countdown_tasks) + len(self.reminder_tasks)
        if total_tasks >= 10:
            show_center_messagebox("任务数量限制", "当前任务列表最多只能添加10条任务，请先删除部分任务后再添加！")
            return
        
        # 1. 输入验证
        name = self.reminder_name_entry.get().strip()
        if not name:
            show_center_messagebox("输入提示", "提醒名称不能为空！")
            return
        
        try:
            # 获取选择的日期时间
            year = int(self.reminder_year.get())
            month = int(self.reminder_month.get())
            day = int(self.reminder_day.get())
            hour = int(self.reminder_hour.get())
            minute = int(self.reminder_minute.get())
            second = int(self.reminder_second.get())
            
            # 计算目标时间
            import datetime
            target_time = datetime.datetime(year, month, day, hour, minute, second)
            current_time = datetime.datetime.now()
            
            # 计算时间差（秒）
            time_diff = (target_time - current_time).total_seconds()
            
            if time_diff <= 0:
                show_center_messagebox("输入提示", "提醒时间必须在当前时间之后！")
                return
                
        except ValueError:
            show_center_messagebox("输入提示", "请输入有效的日期时间！")
            return
        
        # 2. 创建任务行
        task_row = ttk.Frame(self.scrollable_frame, style="Reminder.TFrame")
        task_row.pack(fill=tk.X, pady=0, ipady=8, padx=0)
        
        # 创建内部框架来控制布局
        inner_frame = ttk.Frame(task_row, style="Reminder.TFrame")
        inner_frame.pack(fill=tk.X, expand=True, padx=5)
        
        # 配置三列布局，使用固定宽度
        inner_frame.columnconfigure(0, minsize=400)  # 任务名称固定宽度
        inner_frame.columnconfigure(1, minsize=150)  # 时间固定宽度
        inner_frame.columnconfigure(2, minsize=200)  # 按钮区固定宽度
        inner_frame.rowconfigure(0, weight=1)  # 行占满高度
        
        # 任务名称（标记为提醒） - 与表头对齐
        name_label = ttk.Label(inner_frame, text=f"[定时提醒] {name}", style="Reminder.TLabel", anchor=tk.W, width=30)
        name_label.grid(row=0, column=0, sticky="w", padx=5)
        
        # 剩余时间 - 与表头对齐（居中）
        remaining_label = ttk.Label(inner_frame, text=self.format_time(int(time_diff)), style="Reminder.TLabel", anchor=tk.CENTER, width=10)
        remaining_label.grid(row=0, column=1, sticky="we", padx=5)
        
        # 3. 存储任务信息
        reminder_info = {
            "name": name,
            "target_time": target_time,
            "remaining_seconds": int(time_diff),
            "thread": None,
            "label": remaining_label,
            "row": task_row,
            "running": True
        }
        self.reminder_tasks.append(reminder_info)
        
        # 按钮区框架
        button_frame = ttk.Frame(inner_frame, style="Reminder.TFrame")
        button_frame.grid(row=0, column=2, sticky="we", padx=5)
        
        # 删除按钮
        delete_btn = ttk.Button(button_frame, text="删除", command=lambda r=task_row, info=reminder_info: self.delete_reminder(r, info), width=10)
        delete_btn.pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # 复制按钮
        copy_btn = ttk.Button(button_frame, text="复制", command=lambda info=reminder_info: self.copy_reminder(info), width=10, style="Copy.TButton")
        copy_btn.pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # 任务将由 update_tasks 方法统一处理
        
        # 清空输入框（恢复默认名称）
        self.reminder_name_entry.delete(0, tk.END)
        self.reminder_name_entry.insert(0, "我的定时提醒")

    def show_alert(self, task_name, task_type="countdown", task_info=None):
        """右下角滑入提醒窗口（优化样式）"""
        # 根据任务类型设置颜色
        if task_type == "reminder":
            bg_color = "#22c55e"  # 绿色，用于定时提醒
            title_text = "🔔 定时提醒"
        else:
            bg_color = "#3b82f6"  # 蓝色，用于倒计时
            title_text = "⏰ 倒计时结束"

        # 创建提醒窗口 - 使用None作为父窗口，使其成为顶级窗口
        alert_win = tk.Toplevel(None)
        alert_win.title("提醒")
        alert_win.overrideredirect(True)
        alert_win.geometry("320x160")
        alert_win.configure(bg=bg_color)
        # 确保提醒窗口总是显示在最前面
        alert_win.attributes('-topmost', True)

        # 提醒内容布局
        content_frame = tk.Frame(alert_win, bg=bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 标题
        title_label = tk.Label(content_frame, text=title_text, 
                               font=("Microsoft YaHei", 14, "bold"), 
                               bg=bg_color, fg="white")
        title_label.pack(pady=(5, 10))

        # 任务名称
        task_label = tk.Label(content_frame, text=f"任务：{task_name}", 
                              font=("Microsoft YaHei", 12), 
                              bg=bg_color, fg="white")
        task_label.pack(pady=5)

        # 关闭按钮
        close_btn = ttk.Button(content_frame, text="关闭", 
                               command=lambda: self.close_alert(alert_win, task_info, task_type))
        close_btn.pack(pady=(10, 5))

        # 直接获取屏幕尺寸，不依赖主窗口
        import ctypes
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        
        win_width = 320
        win_height = 160
        target_x = screen_width - win_width - 30
        # 计算垂直偏移量，实现层叠效果
        target_y = screen_height - win_height - 30 - (len(self.alert_windows) * 20)
        start_x = screen_width

        # 滑入动画
        def slide_in(current_x):
            if current_x > target_x:
                new_x = current_x - 8
                alert_win.geometry(f"{win_width}x{win_height}+{new_x}+{target_y}")
                alert_win.after(15, slide_in, new_x)
            else:
                alert_win.geometry(f"{win_width}x{win_height}+{target_x}+{target_y}")
                # 动画完成后将提醒窗口置于顶层
                alert_win.lift()
                alert_win.focus_force()
                alert_win.attributes('-topmost', True)  # 置于顶层
                alert_win.update()
                alert_win.attributes('-topmost', False)  # 取消顶层设置，避免一直置顶

        slide_in(start_x)
        
        # 将提醒窗口添加到列表中
        self.alert_windows.append(alert_win)
        


    def close_alert(self, alert_win, task_info=None, task_type=None):
        """关闭提醒窗口"""
        try:
            alert_win.destroy()
            # 从提醒窗口列表中移除
            if alert_win in self.alert_windows:
                self.alert_windows.remove(alert_win)
            
            # 如果有任务信息，提供复制任务的选项
            if task_info and task_type:
                # 延迟显示复制对话框，避免事件处理冲突
                self.root.after(100, lambda: self.copy_task_from_alert(task_info, task_type))
                # 延迟移除任务，确保复制操作完成
                self.root.after(500, lambda: self.remove_completed_task(task_info, task_type))
            
            # 显示主窗口
            self.show_window()
        except Exception as e:
            print(f"关闭提醒窗口失败: {e}")
    
    def update_scrollable_frame(self):
        """更新滚动区域，确保删除任务后没有残留背景色"""
        # 取消之前的更新请求，避免累积
        if hasattr(self, '_scroll_update_id'):
            self.root.after_cancel(self._scroll_update_id)
        # 延迟更新滚动区域，避免频繁更新
        self._scroll_update_id = self.root.after(100, self._do_update_scrollable_frame)

    def _do_update_scrollable_frame(self):
        """实际执行滚动区域更新"""
        try:
            self.scrollable_frame.update_idletasks()
            self.task_canvas.configure(scrollregion=self.task_canvas.bbox("all"))
        except Exception as e:
            print(f"更新滚动区域失败: {e}")

    def init_tray_icon(self):
        """延迟初始化托盘图标"""
        pass  # 托盘图标将在需要时创建

    def create_tray_icon(self):
        """创建托盘图标"""
        try:
            # 尝试使用 favicon.ico 作为托盘图标
            import os
            import sys
            
            # 获取应用程序运行目录
            if getattr(sys, 'frozen', False):
                # 打包后的环境
                if hasattr(sys, '_MEIPASS'):
                    # 使用 PyInstaller 的临时目录
                    script_dir = sys._MEIPASS
                else:
                    # 回退到可执行文件目录
                    script_dir = os.path.dirname(sys.executable)
            else:
                # 开发环境
                script_dir = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(script_dir, 'favicon.ico')
            
            if os.path.exists(icon_path):
                try:
                    # 使用现有图标
                    image = Image.open(icon_path)
                except Exception:
                    # 创建一个简单的图标作为备用
                    image = Image.new('RGB', (64, 64), color='#3b82f6')
                    draw = ImageDraw.Draw(image)
                    draw.text((15, 15), "⏰", font=None, fill='white')
            else:
                # 创建一个简单的图标作为备用
                image = Image.new('RGB', (64, 64), color='#3b82f6')
                draw = ImageDraw.Draw(image)
                draw.text((15, 15), "⏰", font=None, fill='white')
            
            # 创建托盘菜单
            menu = pystray.Menu(
                pystray.MenuItem("显示窗口", self.show_window),
                pystray.MenuItem("显示悬浮窗", self.create_floating_window),
                pystray.MenuItem("退出", self.exit_app)
            )
            
            # 创建托盘图标
            self.tray_icon = pystray.Icon("countdown_app", image, "多任务倒计时工具", menu)
            
            # 启动托盘图标在单独的线程中
            def run_tray():
                try:
                    # 运行托盘图标
                    self.tray_icon.run()
                except Exception:
                    pass
                finally:
                    # 托盘图标停止后释放资源
                    if self.tray_icon:
                        self.tray_icon = None
            
            # 启动托盘图标线程
            tray_thread = threading.Thread(target=run_tray, daemon=True)
            tray_thread.start()
        except Exception:
            pass

    def on_minimize(self, event):
        """处理窗口最小化事件"""
        # 检查是否是最小化事件
        if event.widget == self.root and event.type == tk.EventType.Unmap:
            # 隐藏窗口
            self.root.withdraw()
            # 创建并显示托盘图标
            if not self.tray_icon:
                # 直接创建托盘图标
                self.create_tray_icon()

    def on_close(self):
        """处理窗口关闭事件，最小化到托盘"""
        # 隐藏窗口
        self.root.withdraw()
        # 创建并显示托盘图标
        if not self.tray_icon:
            # 直接创建托盘图标
            self.create_tray_icon()

    def show_window(self):
        """从托盘恢复窗口"""
        try:
            # 显示窗口
            self.root.deiconify()
            # 激活窗口并置于顶层
            self.root.lift()
            self.root.focus_force()
            self.root.attributes('-topmost', True)  # 置于顶层
            self.root.update()
            self.root.attributes('-topmost', False)  # 取消顶层设置，避免一直置顶
            # 隐藏悬浮窗
            self.hide_floating_window()
            # 停止托盘图标
            if self.tray_icon:
                try:
                    self.tray_icon.stop()
                except Exception as e:
                    print(f"停止托盘图标失败: {e}")
                finally:
                    self.tray_icon = None
        except Exception as e:
            print(f"显示窗口失败: {e}")
    
    def create_floating_window(self):
        """创建独立的悬浮窗窗口，彻底解决闪烁问题"""
        try:
            # 检查悬浮窗是否已存在
            if hasattr(self, 'floating_window') and self.floating_window.winfo_exists():
                # 如果已存在，显示并置于顶层
                self.floating_window.lift()
                self.floating_window.attributes('-topmost', True)
                self.floating_window.update()
                self.floating_window.attributes('-topmost', False)
                return
            
            # 先计算窗口位置
            window_width = 400
            window_height = 500
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            # 计算右下角位置，留出一些边距
            x = screen_width - window_width - 20
            y = screen_height - window_height - 80  # 留出任务栏高度
            
            # 创建一个Toplevel窗口作为悬浮窗
            # 使用更优化的方式避免闪烁问题
            self.floating_window = tk.Toplevel(self.root)
            # 先设置为隐藏状态
            self.floating_window.withdraw()
            # 设置窗口属性
            self.floating_window.title("任务列表")
            self.floating_window.overrideredirect(True)  # 无边框
            self.floating_window.attributes('-topmost', True)  # 置于顶层
            self.floating_window.attributes('-alpha', 0.95)  # 半透明效果
            
            # 直接在指定位置创建窗口
            self.floating_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            # 强制更新窗口位置和大小
            self.floating_window.update_idletasks()
            # 显示窗口
            self.floating_window.deiconify()
            
            # 亮色风格设计
            # 设置背景色为亮色
            self.floating_window.configure(bg="#ffffff")
            
            # 创建亮色风格的自定义样式
            floating_style = ttk.Style(self.floating_window)
            floating_style.theme_use("clam")
            
            # 标题标签样式
            floating_style.configure("Finance.Title.TLabel", 
                                  font=("Microsoft YaHei", 12, "bold"),
                                  foreground="#333333",
                                  background="#ffffff")
            
            # 隐藏按钮样式
            floating_style.configure("Finance.TButton", 
                                  font=("Microsoft YaHei", 10, "bold"),
                                  background="#f0f0f0",
                                  foreground="#333333",
                                  padding=6)
            floating_style.map("Finance.TButton",
                             background=[("active", "#e0e0e0")])
            
            # 创建主框架
            main_frame = ttk.Frame(self.floating_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
            
            # 创建标题栏
            title_frame = ttk.Frame(main_frame)
            title_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # 标题 - 金融风格字体
            title_label = ttk.Label(title_frame, text="多任务倒计时工具", style="Finance.Title.TLabel")
            title_label.pack(side=tk.LEFT, padx=5)
            
            # 隐藏按钮 - 金融风格，使用lambda确保正确调用
            hide_btn = ttk.Button(title_frame, text="隐藏", command=lambda: self.hide_floating_window(), width=8, style="Finance.TButton")
            hide_btn.pack(side=tk.RIGHT, padx=5)
            
            # 创建任务列表框架
            task_frame = ttk.Frame(main_frame)
            task_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
            
            # 创建任务列表，使用亮色风格样式
            self.task_listbox = tk.Listbox(
                task_frame, 
                font=("Microsoft YaHei", 12),  # 加大字体，使用微软雅黑
                selectbackground="#3b82f6", 
                selectforeground="white",
                bg="#f8f9fa",  # 亮色背景
                fg="#333333",  # 深色文字
                relief="flat",  # 平坦效果
                bd=0,
                highlightthickness=0,
                activestyle="none"
            )
            
            # 添加亮色风格的滚动条
            # 配置滚动条样式
            floating_style.configure("Finance.Vertical.TScrollbar",
                                  background="#e0e0e0",
                                  troughcolor="#f8f9fa",
                                  arrowcolor="#666666",
                                  bordercolor="#d0d0d0",
                                  relief="flat")
            
            scrollbar = ttk.Scrollbar(task_frame, orient=tk.VERTICAL, command=self.task_listbox.yview, style="Finance.Vertical.TScrollbar")
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.task_listbox.config(yscrollcommand=scrollbar.set)
            
            # 调整任务列表的pack方式，确保滚动条正确显示
            self.task_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
            
            # 存储滚动条引用
            self.scrollbar = scrollbar
            
            # 更新任务列表
            self.update_task_list()
            
            # 显示窗口
            self.floating_window.deiconify()
            
            # 定时更新任务列表
            self.floating_window.after(1000, self.update_task_list)
            
        except Exception as e:
            print(f"创建悬浮窗失败: {e}")
    
    def update_task_list(self):
        """更新任务列表"""
        try:
            if not hasattr(self, 'task_listbox') or not self.task_listbox.winfo_exists():
                return
            
            # 清空列表
            self.task_listbox.delete(0, tk.END)
            
            # 计算任务总数
            total_tasks = len(self.countdown_tasks) + len(self.reminder_tasks)
            
            # 如果没有任务，显示提示信息
            if total_tasks == 0:
                self.task_listbox.insert(tk.END, "📋 暂无任务")
                self.task_listbox.itemconfig(0, {'fg': '#999999'})  # 亮色风格灰色
            else:
                # 添加倒计时任务
                for task_info in self.countdown_tasks:
                    if task_info.get("running", False):
                        remaining = int(task_info.get("remaining_seconds", 0))
                        task_name = task_info.get("name", "未知任务")
                        status = f"⏰ [倒计提醒] {task_name}"
                        time_str = f"剩余: {self.format_time(remaining)}"
                        # 使用任务对象中存储的target_time
                        target_time = task_info.get("target_time")
                        if target_time:
                            # 只显示时间部分，不显示日期
                            target_str = f"目标时间: {target_time.strftime('%H:%M:%S')}"
                        else:
                            # 如果没有target_time，使用当前时间 + 剩余秒数作为备用
                            import datetime
                            target_time = datetime.datetime.now() + datetime.timedelta(seconds=remaining)
                            target_str = f"目标时间: {target_time.strftime('%H:%M:%S')}"
                        self.task_listbox.insert(tk.END, status)
                        self.task_listbox.insert(tk.END, time_str)
                        self.task_listbox.insert(tk.END, target_str)
                        # 设置颜色 - 亮色风格
                        last_idx = self.task_listbox.size() - 1
                        self.task_listbox.itemconfig(last_idx - 2, {'fg': '#3b82f6'})  # 蓝色
                        self.task_listbox.itemconfig(last_idx - 1, {'fg': '#666666'})  # 灰色
                        self.task_listbox.itemconfig(last_idx, {'fg': '#999999'})  # 浅灰色
                        # 添加空行作为分隔
                        self.task_listbox.insert(tk.END, "")
                
                # 添加提醒任务
                for reminder_info in self.reminder_tasks:
                    if reminder_info.get("running", False):
                        remaining = int(reminder_info.get("remaining_seconds", 0))
                        task_name = reminder_info.get("name", "未知任务")
                        status = f"🔔 [定时提醒] {task_name}"
                        time_str = f"剩余: {self.format_time(remaining)}"
                        # 获取目标时间
                        import datetime
                        target_time = reminder_info.get("target_time", datetime.datetime.now())
                        # 只显示时间部分，不显示日期
                        target_str = f"目标时间: {target_time.strftime('%H:%M:%S')}"
                        self.task_listbox.insert(tk.END, status)
                        self.task_listbox.insert(tk.END, time_str)
                        self.task_listbox.insert(tk.END, target_str)
                        # 设置颜色 - 亮色风格
                        last_idx = self.task_listbox.size() - 1
                        self.task_listbox.itemconfig(last_idx - 2, {'fg': '#22c55e'})  # 绿色
                        self.task_listbox.itemconfig(last_idx - 1, {'fg': '#666666'})  # 灰色
                        self.task_listbox.itemconfig(last_idx, {'fg': '#999999'})  # 浅灰色
                        # 添加空行作为分隔
                        self.task_listbox.insert(tk.END, "")
            
            # 自动显示/隐藏滚动条
            if hasattr(self, 'scrollbar'):
                try:
                    # 检查任务列表是否需要滚动
                    self.task_listbox.update_idletasks()
                    if self.task_listbox.winfo_exists():
                        # 获取任务列表的高度和内容高度
                        listbox_height = self.task_listbox.winfo_height()
                        content_height = self.task_listbox.bbox(tk.END)[3] if self.task_listbox.size() > 0 else 0
                        
                        # 如果内容高度大于列表框高度，显示滚动条
                        if content_height > listbox_height:
                            if not self.scrollbar.winfo_ismapped():
                                self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                        else:
                            # 否则隐藏滚动条
                            if self.scrollbar.winfo_ismapped():
                                self.scrollbar.pack_forget()
                except Exception as e:
                    print(f"调整滚动条失败: {e}")
            
            # 再次定时更新
            if hasattr(self, 'floating_window') and self.floating_window.winfo_exists():
                self.floating_window.after(1000, self.update_task_list)
        except Exception as e:
            print(f"更新任务列表失败: {e}")
    
    def hide_floating_window(self):
        """隐藏悬浮窗"""
        try:
            if hasattr(self, 'floating_window') and self.floating_window.winfo_exists():
                self.floating_window.destroy()
                delattr(self, 'floating_window')
        except Exception as e:
            print(f"隐藏悬浮窗失败: {e}")





    def remove_completed_task(self, task_info, task_type):
        """移除已完成的任务，释放内存"""
        try:
            # 从相应的任务列表中移除
            if task_type == "countdown" and task_info in self.countdown_tasks:
                self.countdown_tasks.remove(task_info)
            elif task_type == "reminder" and task_info in self.reminder_tasks:
                self.reminder_tasks.remove(task_info)
            
            # 销毁任务行
            if "row" in task_info:
                try:
                    task_info["row"].destroy()
                except Exception as e:
                    print(f"销毁任务行失败: {e}")
                del task_info["row"]
            
            # 清理任务对象中的引用
            if "future" in task_info:
                del task_info["future"]
            if "label" in task_info:
                del task_info["label"]
            
            # 延迟更新滚动区域，确保任务移除操作完成后再更新
            self.root.after(300, self.update_scrollable_frame)
        except Exception as e:
            print(f"移除任务失败: {e}")

    def save_tasks(self):
        """保存任务存档"""
        try:
            # 获取存档文件路径
            if getattr(sys, 'frozen', False):
                # 在打包环境中，使用可执行文件所在的目录
                script_dir = os.path.dirname(sys.executable)
            else:
                script_dir = os.path.dirname(os.path.abspath(__file__))
            save_path = os.path.join(script_dir, 'tasks.json')
            
            # 收集任务信息
            tasks_data = {
                "countdown_tasks": [],
                "reminder_tasks": []
            }
            
            # 保存倒计时任务
            import datetime
            save_time = datetime.datetime.now()
            for task in self.countdown_tasks:
                if task.get("running", False) and task.get("remaining_seconds", 0) > 0:
                    task_data = {
                        "name": task.get("name"),
                        "total_seconds": task.get("total_seconds"),
                        "remaining_seconds": task.get("remaining_seconds"),
                        "type": "countdown",
                        "save_time": save_time.isoformat()
                    }
                    tasks_data["countdown_tasks"].append(task_data)
            
            # 保存提醒任务
            for task in self.reminder_tasks:
                if task.get("running", False) and task.get("remaining_seconds", 0) > 0:
                    task_data = {
                        "name": task.get("name"),
                        "target_time": task.get("target_time").isoformat() if "target_time" in task else None,
                        "remaining_seconds": task.get("remaining_seconds"),
                        "type": "reminder",
                        "save_time": save_time.isoformat()
                    }
                    tasks_data["reminder_tasks"].append(task_data)
            
            # 保存到文件
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"保存任务失败: {e}")

    def load_tasks(self):
        """加载任务存档"""
        try:
            # 获取存档文件路径
            if getattr(sys, 'frozen', False):
                # 在打包环境中，使用可执行文件所在的目录
                script_dir = os.path.dirname(sys.executable)
            else:
                script_dir = os.path.dirname(os.path.abspath(__file__))
            save_path = os.path.join(script_dir, 'tasks.json')
            
            # 检查文件是否存在
            if not os.path.exists(save_path):
                return
            
            # 读取存档文件
            with open(save_path, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
            
            # 加载倒计时任务
            import datetime
            current_time = datetime.datetime.now()
            
            for task_data in tasks_data.get("countdown_tasks", []):
                remaining_seconds = task_data.get("remaining_seconds", 0)
                save_time_str = task_data.get("save_time")
                
                # 计算实际剩余时间
                actual_remaining = remaining_seconds
                
                # 如果有保存时间，计算保存到现在的时间差
                if save_time_str:
                    try:
                        save_time = datetime.datetime.fromisoformat(save_time_str)
                        time_diff = (current_time - save_time).total_seconds()
                        # 减去保存到现在的时间差
                        actual_remaining = max(0, remaining_seconds - time_diff)
                    except Exception as e:
                        print(f"解析保存时间失败: {e}")
                
                # 检查是否超过10秒
                if actual_remaining <= 10:
                    actual_remaining = 0
                
                # 创建任务行
                task_row = ttk.Frame(self.scrollable_frame, style="Countdown.TFrame")
                task_row.pack(fill=tk.X, pady=0, ipady=8, padx=0)

                # 创建内部框架
                inner_frame = ttk.Frame(task_row, style="Countdown.TFrame")
                inner_frame.pack(fill=tk.X, expand=True, padx=5)
                
                # 配置布局
                inner_frame.columnconfigure(0, minsize=400)
                inner_frame.columnconfigure(1, minsize=150)
                inner_frame.columnconfigure(2, minsize=200)
                inner_frame.rowconfigure(0, weight=1)

                # 任务名称
                name_label = ttk.Label(inner_frame, text=f"[倒计提醒] {task_data.get('name')}", style="Countdown.TLabel", anchor=tk.W, width=30)
                name_label.grid(row=0, column=0, sticky="w", padx=5)

                # 检查是否已过期
                if actual_remaining <= 0:
                    # 已过期，显示时间到
                    remaining_label = ttk.Label(inner_frame, text="✅ 时间到！", style="Countdown.TLabel", anchor=tk.CENTER, width=10, foreground="#dc2626")
                    task_running = False
                else:
                    # 未过期，显示剩余时间
                    remaining_label = ttk.Label(inner_frame, text=self.format_time(actual_remaining), style="Countdown.TLabel", anchor=tk.CENTER, width=10)
                    task_running = True
                
                remaining_label.grid(row=0, column=1, sticky="we", padx=5)

                # 存储任务信息
                import datetime
                import time
                # 计算目标时间：当前时间 + 实际剩余时间
                target_time = datetime.datetime.now() + datetime.timedelta(seconds=actual_remaining)
                # 计算开始时间：当前时间 - (总时长 - 实际剩余时间)
                start_time = time.time() - (task_data.get('total_seconds', actual_remaining) - actual_remaining)
                task_info = {
                    "name": task_data.get('name'),
                    "total_seconds": task_data.get('total_seconds'),
                    "remaining_seconds": actual_remaining,
                    "target_time": target_time,
                    "start_time": start_time,
                    "thread": None,
                    "label": remaining_label,
                    "row": task_row,
                    "running": task_running
                }
                self.countdown_tasks.append(task_info)

                # 按钮区
                button_frame = ttk.Frame(inner_frame, style="Countdown.TFrame")
                button_frame.grid(row=0, column=2, sticky="we", padx=5)
                
                # 删除按钮
                delete_btn = ttk.Button(button_frame, text="删除", command=lambda r=task_row, info=task_info: self.delete_countdown(r, info), width=10)
                delete_btn.pack(side=tk.LEFT, padx=5, fill=tk.Y)
                
                # 复制按钮
                copy_btn = ttk.Button(button_frame, text="复制", command=lambda info=task_info: self.copy_task(info), width=10, style="Copy.TButton")
                copy_btn.pack(side=tk.LEFT, padx=5, fill=tk.Y)
            
            # 加载提醒任务
            for task_data in tasks_data.get("reminder_tasks", []):
                # 计算实际剩余时间
                import datetime
                target_time = datetime.datetime.fromisoformat(task_data.get('target_time')) if task_data.get('target_time') else None
                actual_remaining = 0
                
                if target_time:
                    time_diff = (target_time - current_time).total_seconds()
                    actual_remaining = max(0, time_diff)
                
                # 检查是否超过10秒
                if actual_remaining <= 10:
                    actual_remaining = 0
                
                # 创建任务行
                task_row = ttk.Frame(self.scrollable_frame, style="Reminder.TFrame")
                task_row.pack(fill=tk.X, pady=0, ipady=8, padx=0)

                # 创建内部框架
                inner_frame = ttk.Frame(task_row, style="Reminder.TFrame")
                inner_frame.pack(fill=tk.X, expand=True, padx=5)
                
                # 配置布局
                inner_frame.columnconfigure(0, minsize=400)
                inner_frame.columnconfigure(1, minsize=150)
                inner_frame.columnconfigure(2, minsize=200)
                inner_frame.rowconfigure(0, weight=1)

                # 任务名称
                name_label = ttk.Label(inner_frame, text=f"[定时提醒] {task_data.get('name')}", style="Reminder.TLabel", anchor=tk.W, width=30)
                name_label.grid(row=0, column=0, sticky="w", padx=5)

                # 检查是否已过期
                if actual_remaining <= 0:
                    # 已过期，显示时间到
                    remaining_label = ttk.Label(inner_frame, text="✅ 时间到！", style="Reminder.TLabel", anchor=tk.CENTER, width=10, foreground="#dc2626")
                    task_running = False
                else:
                    # 未过期，显示剩余时间
                    remaining_label = ttk.Label(inner_frame, text=self.format_time(actual_remaining), style="Reminder.TLabel", anchor=tk.CENTER, width=10)
                    task_running = True
                
                remaining_label.grid(row=0, column=1, sticky="we", padx=5)

                # 存储任务信息
                task_info = {
                    "name": task_data.get('name'),
                    "target_time": target_time,
                    "remaining_seconds": actual_remaining,
                    "thread": None,
                    "label": remaining_label,
                    "row": task_row,
                    "running": task_running
                }
                self.reminder_tasks.append(task_info)

                # 按钮区
                button_frame = ttk.Frame(inner_frame, style="Reminder.TFrame")
                button_frame.grid(row=0, column=2, sticky="we", padx=5)
                
                # 删除按钮
                delete_btn = ttk.Button(button_frame, text="删除", command=lambda r=task_row, info=task_info: self.delete_reminder(r, info), width=10)
                delete_btn.pack(side=tk.LEFT, padx=5, fill=tk.Y)
                
                # 复制按钮
                copy_btn = ttk.Button(button_frame, text="复制", command=lambda info=task_info: self.copy_reminder(info), width=10, style="Copy.TButton")
                copy_btn.pack(side=tk.LEFT, padx=5, fill=tk.Y)
            
            # 更新滚动区域
            self.update_scrollable_frame()
            
        except Exception as e:
            print(f"加载任务失败: {e}")

    def exit_app(self):
        """从托盘退出应用"""
        # 停止任务更新线程
        self.running = False
        # 保存任务存档
        self.save_tasks()
        # 停止所有任务
        for task in self.countdown_tasks:
            task["running"] = False
        for task in self.reminder_tasks:
            task["running"] = False
        # 关闭悬浮窗
        self.hide_floating_window()
        # 停止托盘图标
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None  # 明确设置为 None
        # 关闭窗口
        self.root.destroy()

if __name__ == "__main__":
    # 检查是否已经有实例在运行
    if not singleton():
        # 已经有实例在运行，显示提示并退出
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, "多任务倒计时工具已经在运行中！", "提示", 0)
        sys.exit()
    
    root = tk.Tk()
    app = CountdownApp(root)
    root.mainloop()