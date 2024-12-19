import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import datetime
from tkinter import ttk
import time
import random

# txt文件路径
kucun_path = 'files/kucun.txt'
event_log_path = 'files/event_log.txt'
modify_inventory_log_path = 'files/modify_inventory_log.txt'
users_path = 'files/users.txt'

# 生成唯一ID
def generate_id(prefix='ID'):
    return f'{prefix}_{int(time.time())}{random.randint(1000, 9999)}'


# 读取用户文件
def load_users():
    users = {}
    if os.path.exists(f'{users_path}'):
        with open(f'{users_path}', 'r', encoding='utf-8') as file:
            for line in file:
                id, name, password = line.strip().split('|@|')
                users[id] = {'name': name, 'password': password}
    return users

# 读取库存文件
def load_kucun():
    kucun = []
    with open(kucun_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines[1:]:
            name, id, num, comment = line.strip().split('|@|')
            kucun.append([name, id, num, comment])
    return kucun

def verify_user(id, password):
    users = load_users()
    print(users)
    if id in users and users[id]['password'].strip() == password:
        return [id, users[id]['name'].strip()]
    return False

# 库存管理
# 添加物品操作
def add_item(item_name, quantity):
    with open(f'{item_name}.txt', 'a') as file:
        file.write(f'{datetime.datetime.now()}, +{quantity}\n')

# 删除物品操作
def remove_item(item_name, quantity):
    with open(f'{item_name}.txt', 'a') as file:
        file.write(f'{datetime.datetime.now()}, -{quantity}\n')

# 修改物品操作 -> 通过此操作进行添加数量和减少数量
def modify_item(myself, item_name, quantity, type='add', index=0, parent=None):
    # 验证操作人员，验证通过才能进行操作
    verify_result = verify_user_ui(parent)
    if not verify_result:
        return
     
    # 1、操作库存数量文件
    # 先读取文件，再写入
    
    # # 修正格式代码
    # data = []
    # for i in range(1, len(lines)):
    #     data.append(lines[i].split(','))
    #     print(data[0])
    #     for j in range(len(data[i-1])):
    #         data[i-1][j] = data[i-1][j].strip()
    # print(data)
    # 判断逻辑
    if type == 'add':
        # 修改库存数量
        myself.kucun[index][2] = ' ' + str(int(myself.kucun[index][2]) + int(quantity))
    elif type == 'remove':
        # 修改库存数量
        myself.kucun[index][2] = ' ' + str(int(myself.kucun[index][2]) - int(quantity))
    
    # 写入文件
    with open(kucun_path, 'w', encoding='utf-8') as file:
        file.write("name|@| id|@| num|@| command\n")
        for row in myself.kucun:
            # file.write(f"{row[0]}|@|{row[1]}|@|{row[2]}\n")
            w_str = ""+row[0]
            for i in range(1,len(row)):
                w_str += "|@|"+row[i]
            file.write(w_str+"\n")
    if type == 'add':
        # 2、对此次操作进行记录，记录到事件操作表和修改库存表
        with open(f'{event_log_path}', 'a', encoding='utf-8') as file:
            # 记录事件操作  （事件描述, 操作员工id, 操作员工, 变更内容, 操作时间）
            file.write(f'添加物品|@| {verify_result[0]}|@| {verify_result[1]}|@| 货物: {item_name}, 从{int(myself.kucun[index][2]) - int(quantity)}修改为{myself.kucun[index][2]}|@| {datetime.datetime.now()}\n')
        with open(f'{modify_inventory_log_path}', 'a', encoding='utf-8') as file:
            # 记录库存变更  （物品名称|@| 修改类型|@| 修改数量|@| 修改后数量|@| 操作员工姓名|@| 操作员工ID|@| 修改时间）
            file.write(f'{item_name}|@| add|@| {quantity}|@| {myself.kucun[index][2]}|@| {verify_result[1]}|@| {verify_result[0]}|@| {datetime.datetime.now()}\n')
            
    elif type == 'remove':
        # 2、对此次操作进行记录，记录到事件操作表和修改库存表
        with open(f'{event_log_path}', 'a', encoding='utf-8') as file:
            # 记录事件操作  （事件描述, 操作员工id, 操作员工, 变更内容, 操作时间）
            file.write(f'减少物品|@| {verify_result[0]}|@| {verify_result[1]}|@| 货物: {item_name}, 从{int(myself.kucun[index][2]) + int(quantity)}修改为{myself.kucun[index][2]}|@| {datetime.datetime.now()}\n')
        with open(f'{modify_inventory_log_path}', 'a', encoding='utf-8') as file:
            # 记录库存变更  （物品名称|@| 修改类型|@| 修改数量|@| 修改后数量|@| 操作员工姓名|@| 操作员工ID|@| 修改时间）
            file.write(f'{item_name}|@| remove|@| {quantity}|@| {myself.kucun[index][2]}|@| {verify_result[1]}|@| {verify_result[0]}|@| {datetime.datetime.now()}\n')


# 统计功能
def generate_report(item_name, period='daily'):
    with open(f'{item_name}.txt', 'r') as file:
        lines = file.readlines()
    
    report = {}
    for line in lines:
        date_str, change = line.strip().split('|@| ')
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        
        if period == 'daily':
            key = date.date()
        elif period == 'monthly':
            key = (date.year, date.month)
        elif period == 'quarterly':
            key = (date.year, (date.month-1)//3 + 1)
        elif period == 'yearly':
            key = date.year
        
        if key not in report:
            report[key] = 0
        report[key] += int(change)
    
    return report

# 验证用户->弹出验证用户信息对话框,成功返回用户信息,失败返回False
def verify_user_ui(parent):
    dialog_verify = VerifyDialog(parent,title="验证")
    # dialog_verify.geometry("500x150")
    user_id, password = dialog_verify.get_credentials()

    # 返回信息
    verify_result = verify_user(user_id, password)
    if not verify_result:
        messagebox.showerror("错误", "用户验证失败")
        return False
    else:
        messagebox.showinfo("成功", "用户验证成功")
        return verify_result
    
    # if verify_user(user_id, password):
    #     messagebox.showinfo("成功", "用户验证成功,已修改库存")
    #     return True
    # else:
    #     messagebox.showerror("错误", "用户验证失败")
    #     return False

# 自定义验证用户信息对话框
class VerifyDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None):
        super().__init__(parent, title=title)
    
    def body(self, master):
        tk.Label(master, text="工号:").grid(row=0)
        tk.Label(master, text="密码:").grid(row=1)
        
        self.user_id_entry = tk.Entry(master)
        self.password_entry = tk.Entry(master, show='*')
        
        self.user_id_entry.grid(row=0, column=1)
        self.password_entry.grid(row=1, column=1)
        
        return self.user_id_entry
    
    def apply(self):
        self.user_id = self.user_id_entry.get()
        self.password = self.password_entry.get()
    
    def get_credentials(self):
        return self.user_id, self.password

# GUI
class InventoryApp:
    def __init__(self, root):

        # 获取屏幕宽度和高度
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()

        # 库存
        self.kucun = None

        self.root = root
        self.root.title("寺庙库存管理系统")
        # self.root.geometry("800x500")
        x = (self.screen_width - 800) // 2
        y = (self.screen_height - 500) // 2
        self.root.geometry(f"800x500+{x}+{y}")
        
        self.menu_frame = tk.Frame(root)
        self.menu_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.buttons = {}
        self.create_main_menu()

        # 库存管理页面
        self.tree_inventory = None
        self.inventory_frame = None
        self.dialog_inventory = None

        # 默认显示库存管理页面
        self.show_inventory_management()
    
    def create_main_menu(self):
        # 设置按钮字体
        button_font = ('Arial', 10)
        # 库存管理
        self.buttons['inventory'] = tk.Button(self.menu_frame, text="库存管理", command=self.show_inventory_management, font=button_font)
        self.buttons['inventory'].pack(side=tk.LEFT)
        # 库存类别管理
        self.buttons['category'] = tk.Button(self.menu_frame, text="库存类别管理", command=self.show_category_management, font=button_font)
        self.buttons['category'].pack(side=tk.LEFT)
        # 库存统计功能
        self.buttons['report'] = tk.Button(self.menu_frame, text="库存统计", command=self.show_inventory_report, font=button_font)
        self.buttons['report'].pack(side=tk.LEFT)
        # 员工列表
        self.buttons['employee'] = tk.Button(self.menu_frame, text="员工列表", command=self.show_employee_list, font=button_font)
        self.buttons['employee'].pack(side=tk.LEFT)
    
    # 显示库存管理页面
    def show_inventory_management(self):
        self.clear_frame()
        self.highlight_button('inventory')
        self.create_inventory_management()
    
    # 显示库存类别管理页面
    def show_category_management(self):
        self.clear_frame()
        self.highlight_button('category')
        self.create_category_management()
    
    # 显示员工列表页面
    def show_employee_list(self):
        self.clear_frame()
        self.highlight_button('employee')
        self.create_employee_list()
    
    # 显示库存统计页面
    def show_inventory_report(self):
        self.clear_frame()
        self.highlight_button('report')
        self.create_inventory_report()
    
    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def highlight_button(self, button_key):
        for key, button in self.buttons.items():
            if key == button_key:
                button.config(bg='lightblue')
            else:
                button.config(bg='SystemButtonFace')
    
    # 创建库存管理页面
    def create_inventory_management(self):

        # left_frame = tk.Frame(self.main_frame)
        # left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # right_frame = tk.Frame(self.main_frame)
        # right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 设置主页面
        self.inventory_frame = tk.Frame(self.main_frame)
        self.inventory_frame.pack(fill=tk.BOTH, expand=True)

        # 只需要显示物品名称和库存数量，下标为0和2
        headers = ['物品名称', '库存数量']
        self.kucun = load_kucun()

        # 创建一个Canvas来容纳Treeview
        canvas = tk.Canvas(self.inventory_frame)
        scrollbar = ttk.Scrollbar(self.inventory_frame, orient='vertical')
        scrollbar = ttk.Scrollbar(self.inventory_frame, orient='vertical')
        tree_frame = ttk.Frame(canvas)
        
        # 布局
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        canvas.create_window((0, 0), window=tree_frame, anchor='nw')

        # 创建Treeview表格
        self.tree_inventory = ttk.Treeview(tree_frame, columns=headers, show='headings')
        # # 配置列标题和数据的居中对齐
        # for header in headers:
        #     tree.heading(header, text=header, anchor='center')  # 标题居中
        #     tree.column(header, width=150, anchor='center')  # 数据居中
        for header in headers:
            self.tree_inventory.heading(header, text=header)
        for row in self.kucun:
            # 只需要显示物品名称和库存数量，下标为0和2
            self.tree_inventory.insert('', 'end', values=(row[0], row[2]))
        # 设置居中

        self.tree_inventory.pack(fill=tk.BOTH, expand=True)

        # 绑定tree和Scrollbar
        scrollbar.configure(command=self.tree_inventory.yview)
        self.tree_inventory.configure(yscrollcommand=scrollbar.set)
        # 绑定tree的双击事件
        self.tree_inventory.bind('<Double-1>', self.on_double_click_inventory)

        # 更新Canvas的滚动区域
        tree_frame.update_idletasks()
        tree_frame.pack(fill=tk.BOTH, expand=True)
        canvas.config(scrollregion=canvas.bbox('all'))

    # 双击事件
    def on_double_click_inventory(self, event):
        # 禁止操作主界面
        self.root.attributes("-disabled", True)
        # 获取双击的行
        selected_item = self.tree_inventory.selection()
        if not selected_item:
            return
        # 获取双击行的index
        selected_index = self.tree_inventory.index(selected_item)

        # 获取行数据
        item_values = self.tree_inventory.item(selected_item, "values")
        product_name = item_values[0]  # 产品名称
        product_id = item_values[1]    # 产品ID
        product_quantity = int(item_values[1])  # 库存数量

        # 弹出新窗口
        self.dialog_inventory = tk.Toplevel(self.root)
        self.dialog_inventory.title("库存管理")
        # self.dialog_inventory.geometry("300x150")
        x = (self.screen_width - 300) // 2
        y = (self.screen_height - 150) // 2
        self.dialog_inventory.geometry(f"300x150+{x}+{y}")
        # 设置关闭事件
        self.dialog_inventory.protocol("WM_DELETE_WINDOW", self.on_closing_dialog_inventory)
        # # 设置弹框顶置
        # self.dialog_inventory.attributes("-topmost", True)
        
        # 配置行和列的权重，使它们可以伸缩
        self.dialog_inventory.grid_rowconfigure(0, weight=1)
        self.dialog_inventory.grid_rowconfigure(1, weight=1)
        self.dialog_inventory.grid_rowconfigure(2, weight=1)
        self.dialog_inventory.grid_columnconfigure(0, weight=1)
        self.dialog_inventory.grid_columnconfigure(1, weight=1)

        # 显示产品名称
        tk.Label(self.dialog_inventory, text="产品名称:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        tk.Label(self.dialog_inventory, text=product_name).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # 显示库存数量
        tk.Label(self.dialog_inventory, text="库存数量:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        tk.Label(self.dialog_inventory, text=product_quantity).grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # 输入操作数量
        tk.Label(self.dialog_inventory, text="操作数量:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        quantity_entry = tk.Entry(self.dialog_inventory)
        quantity_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        quantity_entry.config(width=10)
        # 默认值为1
        quantity_entry.insert(0, "1")
        # 只能输入数字

        # 离开焦点事件
        # quantity_entry.bind('<FocusOut>',lambda e: self.on_focus_out_inventory_event(product_quantity, e))
        
        # 第四行加入空白标签 (如果需要)
        tk.Label(self.dialog_inventory, text="").grid(row=3, column=0, columnspan=2)
        
        # 添加按钮
        tk.Button(self.dialog_inventory, text="添加", command=lambda: self.add_product(product_name, product_quantity, quantity_entry.get(), selected_index)).grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        
        # 减少按钮
        tk.Button(self.dialog_inventory, text="减少", command=lambda: self.remove_product(product_name, product_quantity, quantity_entry.get(), selected_index)).grid(row=4, column=1, padx=10, pady=10, sticky="ew")
    
    # 添加产品数量,index为选中的行(从0开始),便于后续修改; 参数解释: product_name:产品名称, product_quantity:产品数量, quantitym:操作数量, index:选中行
    def add_product(self, product_name, product_quantity, quantitym, index):
        # 验证逻辑是否合法
        if not self.logic_verify(product_quantity, quantitym, 'add'):
            return
        # 添加产品数量
        modify_item(self,product_name, quantitym, "add", index, parent=self.root)
        # 刷新页面
        self.show_inventory_management()
        # 关闭弹窗
        self.on_closing_dialog_inventory()
    
    # 减少产品数量
    def remove_product(self, product_name, product_quantity, quantitym, index):
        # 验证逻辑是否合法
        if not self.logic_verify(product_quantity, quantitym, 'remove'):
            return
        # 减少产品数量
        modify_item(self, product_name, quantitym, "remove", index, parent=self.root)
        # 刷新页面
        self.show_inventory_management()
        # 关闭弹窗
        self.on_closing_dialog_inventory()

    # 监听dialog_inventory窗口的关闭事件
    def on_closing_dialog_inventory(self):
        print("关闭弹窗")
        self.root.attributes("-disabled", False)
        # root到顶层
        self.root.attributes("-topmost", True)
        self.dialog_inventory.destroy()
        # root取消顶层
        self.root.attributes("-topmost", False)

    # 修改库存逻辑验证
    def logic_verify(self, product_quantity, quantitym, type):
        print("逻辑验证")
        # 1、验证quantitym是否为数字
        if not quantitym.isdigit():
            messagebox.showerror("错误", "请输入数字")
            return False
        # 2、验证quantitym是否大于0
        if int(quantitym) <= 0:
            messagebox.showerror("错误", "请输入大于0的数字")
            return False
        # 3、验证type是否为add或remove
        if type == 'remove':
            if int(quantitym) > int(product_quantity):
                messagebox.showerror("错误", "减少数量大于库存数量")
                return False
        return True
            
        
        # if not event.widget.get().isdigit():
        #     messagebox.showerror("错误", "请输入数字")
        #     event.widget.delete(0, tk.END)
        #     event.widget.insert(0, 1)
        
        # content = event.widget.get()
        
    
    # 清空库存物品
    def clear_inventory_frame(self):
        for widget in self.inventory_frame.winfo_children():
            widget.destroy()
    
    # 创建库存类别管理页面
    def create_category_management(self):

        # 添加一个新的categoryFrame主页面
        # 定义状态变量，选中的物品坐标
        self.selected_item_index = None

        # 添加一个新的categoryFrame主页面
        self.category_frame = tk.Frame(self.main_frame)
        self.category_frame.pack(fill=tk.BOTH, expand=True)
        # # 设置测试背景颜色
        # self.category_frame.config(bg='red')
        # # 设置测试背景颜色
        # self.category_frame.config(bg='red')

        # 添加两个frame
        self.left_frame_category = tk.Frame(self.category_frame, width=400)
        self.left_frame_category.pack(side=tk.LEFT, padx=(40,0), fill=tk.Y)
        self.right_frame_category = tk.Frame(self.category_frame, width=260)
        self.right_frame_category.pack(side=tk.RIGHT, padx=(0,40), fill=tk.Y)

        # 左侧frame加入view和滑轮
        self.canvas_category = tk.Canvas(self.left_frame_category)
        columns = {"库存物品名称":190,"备注":190}
        self.tree_category = ttk.Treeview(self.canvas_category, columns=list(columns), show='headings')
        self.scrollbar_category = tk.Scrollbar(self.left_frame_category, orient='vertical')
        for text, width in columns.items():  # 批量设置列属性
            self.tree_category.heading(text, text=text, anchor='center')
            self.tree_category.column(text, anchor='center', width=width, stretch=True)  # stretch 不自动拉伸
        self.tree_category.pack(fill=tk.BOTH, expand=True)
        self.canvas_category.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) 
        self.scrollbar_category.pack(side=tk.RIGHT, fill='y')

        # 绑定tree和Scrollbar
        self.scrollbar_category.configure(command=self.tree_category.yview)
        self.tree_category.configure(yscrollcommand=self.scrollbar_category.set)

        # 绑定tree的单击事件
        self.tree_category.bind('<Button-1>', self.on_click_category)
        # 绑定tree的双击事件
        self.tree_category.bind('<Double-1>', self.on_click_double_category)

        # 获取库存数据
        self.kucun = load_kucun()
        # 往tree中插入数据
        for row in self.kucun:
            self.tree_category.insert('', 'end', values=(row[0], row[3]))

        # # 往tree中插入数据->测试
        # for i in range(100):
        #     self.tree_category.insert('', 'end', values=(f'物品{i}', f'备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注备注{i}'))

        # 右侧frame加入标签按钮,按钮宽120，高35
        self.label_category = tk.Label(self.right_frame_category, text="操作按钮", width=20, height=2, font=("Arial", 15, "bold")).pack(side=tk.TOP)
        tk.Button(self.right_frame_category, text="添加物品", command=self.add_item_event, width=20, height=2).pack(side=tk.TOP, pady=(80,30))
        tk.Button(self.right_frame_category, text="删除物品", command=self.remove_item_event, width=20, height=2).pack(side=tk.TOP, pady=30)
        tk.Button(self.right_frame_category, text="修改物品", command=self.modify_item_event, width=20, height=2).pack(side=tk.TOP, pady=30)

    # 类别页面鼠标单击事件
    def on_click_category(self, event):
        # 获取鼠标指针所在行的ID
        row_id = self.tree_category.identify_row(event.y)
        # 获取行数据
        item_data = self.tree_category.item(row_id, "values")

        # 可能选中的是空白处
        if not item_data:
            print('单击选中空白处')
            return
        
        # 获取行的index
        self.selected_item = self.tree_category.index(row_id)
        print('单击选中行：', self.selected_item)
        self.selected_item_index = self.selected_item
    
    # 类别页面鼠标双击事件
    def on_click_double_category(self, event):
        # 获取鼠标指针所在行的ID
        row_id = self.tree_category.identify_row(event.y)
        # 获取行数据
        item_data = self.tree_category.item(row_id, "values")

        # 可能选中的是空白处
        if not item_data:
            print('双击选中空白处')
            return
        
        # 获取行的index
        self.selected_item = self.tree_category.index(row_id)
        print('双击选中行：', self.selected_item)
        # 弹出新窗口，显示详细信息
        self.dialog_category = tk.Toplevel(self.root)
        self.dialog_category.title("物品详细信息")
        self.dialog_category.geometry("300x150")
        # 不可改变大小
        self.dialog_category.resizable(False, False)
        # 禁止操作主界面
        self.root.attributes("-disabled", True)
        # 在屏幕中央显示
        x = (self.screen_width - 300) // 2
        y = (self.screen_height - 150) // 2
        self.dialog_category.geometry(f"300x150+{x}+{y}")
        # # 设置关闭事件
        # self.dialog_category.protocol("WM_DELETE_WINDOW", self.on_closing_dialog_category)
        # # 设置弹框顶置
        self.dialog_category.attributes("-topmost", True)
        # 显示产品名称
        tk.Label(self.dialog_category, text="产品名称:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        tk.Label(self.dialog_category, text=item_data[0]).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        # 显示完整备注，使用文字框，不可编辑
        tk.Label(self.dialog_category, text="备注:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        text = tk.Text(self.dialog_category, width=27, height=8)
        text.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        text.insert(tk.END, item_data[1])
        text.config(state=tk.DISABLED)

        # 接触禁止操作主界面
        self.root.attributes("-disabled", False)


    # 创建员工列表页面
    def create_employee_list(self):
        tk.Label(self.main_frame, text="员工列表页面").pack()
        # 添加员工列表的具体实现

    # 创建库存统计页面
    def create_inventory_report(self):
        tk.Label(self.main_frame, text="库存统计页面").pack()
        # 添加库存统计的具体实现
    
    # 添加物品事件
    def add_item_event(self):
        # if self.verify_user():
        #     item_name = self.item_name.get()
        #     quantity = int(self.item_quantity.get())
        #     add_item(item_name, quantity)
        #     messagebox.showinfo("成功", "添加成功")
        # 弹出添加物品对话框
        self.dialog_add_item_category = tk.Toplevel(self.category_frame)
        self.dialog_add_item_category.title("添加物品")
        self.dialog_add_item_category.geometry("300x150")
        # 配置对话框的列宽权重，让列可以扩展
        self.dialog_add_item_category.grid_columnconfigure(0, weight=1)
        self.dialog_add_item_category.grid_columnconfigure(1, weight=1)
        # 禁止操作主界面
        self.root.attributes("-disabled", True)
        # 在屏幕中央显示
        x = (self.screen_width - 420) // 2
        y = (self.screen_height - 250) // 2
        self.dialog_add_item_category.geometry(f"420x250+{x}+{y}")
        # 物品名称
        tk.Label(self.dialog_add_item_category, text="物品名称:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        item_name = tk.Entry(self.dialog_add_item_category)
        item_name.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        item_name.config(width=10)
        # 数量
        tk.Label(self.dialog_add_item_category, text="数量:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        item_quantity = tk.Entry(self.dialog_add_item_category)
        item_quantity.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        item_quantity.config(width=10)
        # 第三行添加备注
        tk.Label(self.dialog_add_item_category, text="备注：").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        # 添加备注框
        comment_quantity = tk.Text(self.dialog_add_item_category, width=27, height=8)
        comment_quantity.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # 添加按钮
        tk.Button(self.dialog_add_item_category, text="添加", height=2, width=5, command=lambda: self.category_add_commit_item_event(item_name.get(), item_quantity.get(), comment_quantity.get("1.0", "end-1c"))).grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # 解除禁止操作主界面
        self.root.attributes("-disabled", False)
    
    # 提交添加物品事件
    def category_add_commit_item_event(self, item_name, item_quantity, comment_text): 
        # 验证逻辑是否合法
        # 1、验证物品名称是否为空
        if not item_name:
            messagebox.showerror("错误", "请输入物品名称")
            return False
        # 2、验证quantitym是否为数字
        if not item_quantity.isdigit():
            messagebox.showerror("错误", "请输入数字")
            return False
        # 3、验证quantitym是否大于0
        if int(item_quantity) < 0:
            messagebox.showerror("错误", "请输入大于等于0的数字")
            return False
        
        # 生成唯一ID
        id = generate_id('item')
        print('添加物品:', item_name, id, item_quantity, comment_text)
        # 写入库存文件
        with open(kucun_path, 'a', encoding='utf-8') as file:
            file.write(f"{item_name}|@|{id}|@|{item_quantity}|@|{comment_text}\n")
        # 刷新页面
        self.show_category_management()
        # 关闭弹窗
        self.dialog_add_item_category.destroy()
    
    # 删除物品事件
    def remove_item_event(self):
        if self.verify_user():
            item_name = self.item_name.get()
            quantity = int(self.item_quantity.get())
            remove_item(item_name, quantity)
            messagebox.showinfo("成功", "删除成功")
    
    # 修改物品事件
    def modify_item_event(self):
        if self.verify_user():
            item_name = self.item_name.get()
            quantity = int(self.item_quantity.get())
            modify_item(item_name, quantity)
            messagebox.showinfo("成功", "修改成功")
    
    # 生成日报表
    def generate_daily_report(self):
        if self.verify_user():
            item_name = self.item_name.get()
            report = generate_report(item_name, 'daily')
            report_str = "\n".join([f"{key}: {value}" for key, value in report.items()])
            messagebox.showinfo("日报表", report_str)

if __name__ == "__main__":
    root = tk.Tk()
    # 创建 Style 对象
    style = ttk.Style()

    # 配置 Treeview 的字体
    style.configure("Treeview", font=("Arial", 13))  # 设置字体为 Arial，大小为 14
    style.configure("Treeview.Heading", font=("Arial", 13, "bold"))  # 设置表头字体
    # 创建 Style 对象
    style = ttk.Style()

    # 配置 Treeview 的字体
    style.configure("Treeview", font=("Arial", 13))  # 设置字体为 Arial，大小为 14
    style.configure("Treeview.Heading", font=("Arial", 13, "bold"))  # 设置表头字体
    app = InventoryApp(root)
    root.mainloop()