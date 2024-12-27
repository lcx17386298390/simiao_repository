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
items_folder_path = 'files/items/'
user_index_temp_path = 'files/user_index_temp.txt'


# 生成唯一ID
def generate_id(prefix='ID'):
    return f'{prefix}_{int(time.time())}{random.randint(1000, 9999)}'


# 读取用户文件
def load_users():
    users = {}
    if os.path.exists(f'{users_path}'):
        with open(f'{users_path}', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines[1:]:
                id, job_number, name, password = line.strip().split('|@| ')
                users[job_number] = {'id': id, 'name': name, 'password': password}
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

# 获取物品的所有出库入库记录
def get_current_item(item_id):
    item_path = items_folder_path + f"{item_id}.txt"
    current_item_record = []
    with open(item_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines[1:]:
            record = line.strip().split('|@| ')
            current_item_record.append(record)
    return current_item_record

# 得到用户下标标记
def get_user_index_temp():
    if os.path.exists(f'{user_index_temp_path}'):
        with open(f'{user_index_temp_path}', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            return int(lines[0].strip())
    return 0

# 保存用户下标标记
def save_user_index_temp(index):
    with open(f'{user_index_temp_path}', 'w', encoding='utf-8') as file:
        file.write(f'{index}\n')


def verify_user(job_number, password):
    users = load_users()
    if job_number in users and users[job_number]['password'].strip() == password:
        return [job_number, users[job_number]['name'].strip()]
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
        return False
     
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
        # 修改物品表格文件->id.txt【修改类型|@| 修改数量|@| 修改后数量|@| 操作员工姓名|@| 操作员工ID|@| 修改时间  】,在items文件夹下
        with open(f'{items_folder_path}{myself.kucun[index][1]}.txt', 'a', encoding='utf-8') as file:
            file.write(f'add|@| {quantity}|@| {myself.kucun[index][2]}|@| {verify_result[1]}|@| {verify_result[0]}|@| {datetime.datetime.now()}\n')

            
    elif type == 'remove':
        # 2、对此次操作进行记录，记录到事件操作表和修改库存表
        with open(f'{event_log_path}', 'a', encoding='utf-8') as file:
            # 记录事件操作  （事件描述, 操作员工id, 操作员工, 变更内容, 操作时间）
            file.write(f'减少物品|@| {verify_result[0]}|@| {verify_result[1]}|@| 货物: {item_name}, 从{int(myself.kucun[index][2]) + int(quantity)}修改为{myself.kucun[index][2]}|@| {datetime.datetime.now()}\n')
        with open(f'{modify_inventory_log_path}', 'a', encoding='utf-8') as file:
            # 记录库存变更  （物品名称|@| 修改类型|@| 修改数量|@| 修改后数量|@| 操作员工姓名|@| 操作员工ID|@| 修改时间）
            file.write(f'{item_name}|@| remove|@| {quantity}|@| {myself.kucun[index][2]}|@| {verify_result[1]}|@| {verify_result[0]}|@| {datetime.datetime.now()}\n')
        # 修改物品表格文件->id.txt【修改类型|@| 修改数量|@| 修改后数量|@| 操作员工姓名|@| 操作员工ID|@| 修改时间  】,在items文件夹下
        with open(f'{items_folder_path}{myself.kucun[index][1]}.txt', 'a', encoding='utf-8') as file:
            file.write(f'remove|@| {quantity}|@| {myself.kucun[index][2]}|@| {verify_result[1]}|@| {verify_result[0]}|@| {datetime.datetime.now()}\n')
    return True


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
    print("弹出验证用户信息对话框")
    user_id, password = dialog_verify.get_credentials()

    # 返回信息
    verify_result = verify_user(user_id, password)
    if not verify_result:
        messagebox.showerror("错误", "用户验证失败")
        return False
    else:
        # messagebox.showinfo("成功", "用户验证成功")
        print("该用户信息：", verify_result)
        return verify_result


# 自定义验证用户信息对话框
class VerifyDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None):
        self.user_id = None
        self.password = None
        super().__init__(parent, title=title)
    
    def body(self, master):
        tk.Label(master, text="工号:").grid(row=0)
        tk.Label(master, text="密码:").grid(row=1)
        
        self.user_id_entry = tk.Entry(master)
        self.password_entry = tk.Entry(master, show='*')
        
        self.user_id_entry.grid(row=0, column=1)
        self.password_entry.grid(row=1, column=1)

        # 测试添加默认值
        self.user_id_entry.insert(0, "root")
        self.password_entry.insert(0, "1234")
        
        return self.user_id_entry
    
    def apply(self):
        self.user_id = self.user_id_entry.get()
        self.password = self.password_entry.get()
    
    def get_credentials(self):
        if self.user_id and self.password:
            return self.user_id, self.password
        return None, None

# GUI
class InventoryApp:
    def __init__(self, root):

        # 获取屏幕宽度和高度
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()

        # 库存
        self.kucun = None
        # 员工
        self.employee = None

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
        headers = ['','物品名称', '库存数量']
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
        self.tree_inventory.column(headers[0], width=60, minwidth=60, anchor='center', stretch=tk.NO)
        for index, row in enumerate(self.kucun, start=0):
            # 只需要显示物品名称和库存数量，下标为0和2
            self.tree_inventory.insert('', 'end', values=(index+1,row[0], row[2]))
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
        # 获取双击的行
        selected_item = self.tree_inventory.selection()
        if not selected_item:
            return
        # 获取双击行的index
        selected_index = self.tree_inventory.index(selected_item)

        # 获取行数据
        item_values = self.tree_inventory.item(selected_item, "values")
        item_text = self.tree_inventory.item(selected_item, "text")
        print("双击选中行：", selected_index, item_values, item_text)
        product_name = item_values[1]  # 产品名称
        # product_id = self.kucun[selected_index][1]    # 产品ID
        product_quantity = int(item_values[2])  # 库存数量

        # 弹出新窗口
        self.dialog_inventory = tk.Toplevel(self.root)
        self.dialog_inventory.title("库存管理")
        # self.dialog_inventory.geometry("300x150")
        x = (self.screen_width - 300) // 2
        y = (self.screen_height - 150) // 2
        self.dialog_inventory.geometry(f"300x150+{x}+{y}")
        # 禁止操作主界面
        self.root.attributes("-disabled", True)
        # 置于root顶
        self.dialog_inventory.transient(self.root)
        # 设置关闭事件
        self.dialog_inventory.protocol("WM_DELETE_WINDOW", self.on_closing_dialog_inventory)
        
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
        if modify_item(self,product_name, quantitym, "add", index, parent=self.root):
            # 关闭弹窗
            self.on_closing_dialog_inventory()
        # 刷新页面
        self.show_inventory_management()
        # # 关闭弹窗
        # self.on_closing_dialog_inventory()
    
    # 减少产品数量
    def remove_product(self, product_name, product_quantity, quantitym, index):
        # 验证逻辑是否合法
        if not self.logic_verify(product_quantity, quantitym, 'remove'):
            return
        # 减少产品数量
        if modify_item(self, product_name, quantitym, "remove", index, parent=self.root):
            # 关闭弹窗
            self.on_closing_dialog_inventory()
        # 刷新页面
        self.show_inventory_management()
        # # 关闭弹窗
        # self.on_closing_dialog_inventory()

    # 监听dialog_inventory窗口的关闭事件
    def on_closing_dialog_inventory(self):
        print("关闭弹窗")
        self.root.attributes("-disabled", False)
        # 聚焦到主窗口
        self.root.focus_force()
        self.dialog_inventory.destroy()

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
        columns = {"":60, "库存物品名称":190,"备注":190}
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
        # 往tree中插入数据,备注只显示部分
        for index, row in enumerate(self.kucun, start=1):
            self.tree_category.insert('', 'end', values=(index, row[0], row[3][:5]+'...'))

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
        # 聚焦到弹窗
        self.dialog_category.focus_force()
        # 显示产品名称
        tk.Label(self.dialog_category, text="产品名称:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        tk.Label(self.dialog_category, text=item_data[0]).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        # 显示完整备注，使用文字框，不可编辑
        tk.Label(self.dialog_category, text="备注:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        text = tk.Text(self.dialog_category, width=27, height=8)
        text.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        # 显示完整备注
        text.insert(tk.END, self.kucun[self.selected_item_index][3])
        text.config(state=tk.DISABLED)

        # 接触禁止操作主界面
        self.root.attributes("-disabled", False)


    # 创建员工列表页面
    def create_employee_list(self):
        # 员工页面鼠标单击事件
        def on_click_employee(event):
            # 获取鼠标指针所在行的ID
            row_id = self.tree_employee.identify_row(event.y)
            # 获取行数据
            item_data = self.tree_employee.item(row_id, "values")
            # 员工id
            employee_id = self.tree_employee.item(row_id, "text")

            # 可能选中的是空白处
            if not item_data:
                print('单击选中空白处')
                return
            # 获取行的index
            # self.selected_employee = self.tree_employee.index(row_id)
            # print('单击选中行：', self.selected_employee)
            # self.selected_employee_job_number = self.selected_employee
            self.selected_employee_job_number = item_data[0]
            
        # 员工页面鼠标双击事件
        def on_click_double_employee(event):
            # 获取鼠标指针所在行的ID
            row_id = self.tree_employee.identify_row(event.y)
            # 获取行数据
            item_data = self.tree_employee.item(row_id, "values")
            # 员工id
            employee_id = self.tree_employee.item(row_id, "text")

            # 可能选中的是空白处
            if not item_data:
                print('双击选中空白处')
                return
            
            # 获取行的index
            self.selected_employee = self.tree_employee.index(row_id)
            print('双击选中行：', self.selected_employee)
            # 弹出新窗口，显示详细信息
            self.dialog_employee = tk.Toplevel(self.root)
            self.dialog_employee.title("物品详细信息")
            self.dialog_employee.geometry("300x150")
            # 不可改变大小
            self.dialog_employee.resizable(False, False)
            # 禁止操作主界面
            self.root.attributes("-disabled", True)
            # 在屏幕中央显示
            x = (self.screen_width - 300) // 2
            y = (self.screen_height - 150) // 2
            self.dialog_employee.geometry(f"300x150+{x}+{y}")
            # # 设置关闭事件
            # self.dialog_employee.protocol("WM_DELETE_WINDOW", self.on_closing_dialog_employee)
            # 聚焦到弹窗
            self.dialog_employee.focus_force()
            # 显示产品名称
            tk.Label(self.dialog_employee, text="产品名称:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
            tk.Label(self.dialog_employee, text=item_data[0]).grid(row=0, column=1, padx=10, pady=5, sticky="w")
            # 显示完整备注，使用文字框，不可编辑
            tk.Label(self.dialog_employee, text="备注:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
            text = tk.Text(self.dialog_employee, width=27, height=8)
            text.grid(row=1, column=1, padx=10, pady=5, sticky="w")
            # 显示完整备注
            text.insert(tk.END, self.kucun[self.selected_employee_job_number][3])
            text.config(state=tk.DISABLED)

            # 接触禁止操作主界面
            self.root.attributes("-disabled", False)
        
            # 添加物品事件
        
        def add_employee_event():
            # 先弹出验证用户对话框
            verify_result = verify_user_ui(self.root)
            if not verify_result:
                return
            
            # 弹出添加员工对话框
            self.dialog_add_employee = tk.Toplevel(self.employee_frame)
            self.dialog_add_employee.title("添加员工")
            # self.dialog_add_employee.geometry("300x150")
            # 配置对话框的列宽权重，让列可以扩展
            self.dialog_add_employee.grid_columnconfigure(0, weight=1)
            self.dialog_add_employee.grid_columnconfigure(1, weight=1)
            # 设置关闭事件
            self.dialog_add_employee.protocol("WM_DELETE_WINDOW", on_closing_dialog_add_employee)
            # 置于root顶
            self.dialog_add_employee.transient(self.root)
            # 禁止操作主界面
            self.root.attributes("-disabled", True)
            # 在屏幕中央显示
            x = (self.screen_width - 300) // 2
            y = (self.screen_height - 150) // 2
            self.dialog_add_employee.geometry(f"300x150+{x}+{y}")
            # 用户姓名
            tk.Label(self.dialog_add_employee, text="用户姓名:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
            user_name = tk.Entry(self.dialog_add_employee)
            user_name.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
            user_name.config(width=10)
            # 用户密码
            tk.Label(self.dialog_add_employee, text="用户密码:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
            user_pw = tk.Entry(self.dialog_add_employee, show='*')
            user_pw.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
            user_pw.config(width=10)
            # 第三行加入空白标签
            tk.Label(self.dialog_add_employee, text="").grid(row=2, column=0, columnspan=2)

            # 添加按钮
            tk.Button(self.dialog_add_employee, text="添加", height=2, width=5, command=lambda: employee_add_commit_employee_event(user_name.get(), user_pw.get(), verify_result)).grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")


        # 提交添加员工事件
        def employee_add_commit_employee_event(employee_name, employee_password,verify_result): 
            # 验证逻辑是否合法
            if not employee_name:
                messagebox.showerror("错误", "请输入员工姓名")
                return
            if not employee_password:
                messagebox.showerror("错误", "请输入员工密码")
                return
            # 添加员工
            # 生成员工id
            employee_id = generate_id("user")
            # 员工工号-> 88+（user_temp+1）-> 88001,88002,88003...
            user_index_temp = get_user_index_temp()
            save_user_index_temp(user_index_temp+1)
            employee_job_number = 88000 + user_index_temp + 1
            # 添加员工
            self.employee[employee_job_number] = {'id':employee_id, 'name': employee_name, 'password': employee_password}
            # 添加用户
            with open(users_path, 'a', encoding='utf-8') as file:
                file.write(f"{employee_id}|@| {employee_job_number}|@| {employee_name}|@| {employee_password}\n")# id|@| job_number|@| name|@| password
            # 写入事件日志
            with open(event_log_path, 'a', encoding='utf-8') as file:
                file.write(f'添加用户|@| {verify_result[0]}|@| {verify_result[1]}|@| 新建用户姓名: {employee_name}，工号：{employee_job_number}|@| {datetime.datetime.now()}\n')
            
            # 提示添加成功
            messagebox.showinfo("提示", "添加成功")
            # 关闭弹窗
            on_closing_dialog_add_employee()
            # 刷新页面
            self.show_employee_list()
        
        # 提交物品弹窗关闭事件
        def on_closing_dialog_add_employee():
            print("关闭提交弹窗")
            self.root.attributes("-disabled", False)
            # 聚焦到主窗口
            self.root.focus_force()
            self.dialog_add_employee.destroy()
        
        # 删除员工事件
        def remove_employee_event():
            # 检查是否选中物品
            if self.selected_employee_job_number is None:
                messagebox.showerror("错误", "请选择员工")
                return
            # 弹出员工验证对话框
            verify_result = verify_user_ui(self.root)
            if not verify_result:
                return
            # 获取员工信息
            employee_id, employee_name, employee_password = self.employee[self.selected_employee_job_number]['id'], self.employee[self.selected_employee_job_number]['name'], self.employee[self.selected_employee_job_number]['password']
            print('删除员工:', employee_name, employee_password)
            # 删除员工
            self.employee.pop(self.selected_employee_job_number)
            # 写入员工文件
            with open(users_path, 'w', encoding='utf-8') as file:
                # 写入表头
                file.write("id|@| job_number|@| name|@| password\n")
                # 重新写入员工文件
                for job_number, values in self.employee.items():
                    file.write(f"{values['id']}|@| {job_number}|@| {values['name']}|@| {values['password']}\n")
            # 写入事件日志
            with open(event_log_path, 'a', encoding='utf-8') as file:
                file.write(f'删除用户|@| {verify_result[0]}|@| {verify_result[1]}|@| 删除员工姓名: {employee_name}，删除员工工号：{self.selected_employee_job_number}|@| {datetime.datetime.now()}\n')
            # 提示删除成功
            messagebox.showinfo("提示", "删除成功")
            # 刷新页面
            self.show_employee_list()
            # 解除禁止操作主界面
            self.root.attributes("-disabled", False)
            # 聚焦到主窗口
            self.root.focus_force()

        
        # 修改员工事件
        def modify_employee_event():
            # 提交修改员工事件
            def category_modify_commit_employee_event(item_name_entry, comment_text, verify_result): 
                # 原来员工信息
                employee_id, employee_name, employee_password = self.employee[self.selected_employee_job_number]['id'], self.employee[self.selected_employee_job_number]['name'], self.employee[self.selected_employee_job_number]['password']
                print('修改员工:', employee_name, employee_password)

                # 修改员工信息
                self.employee[self.selected_employee_job_number]['name'] = item_name_entry
                self.employee[self.selected_employee_job_number]['password'] = comment_text

                # 写入用户文件
                with open(users_path, 'w', encoding='utf-8') as file:
                    # 写入表头
                    file.write("id|@| job_number|@| name|@| password\n")
                    # 重新写入员工文件
                    for job_number, values in self.employee.items():
                        file.write(f"{values['id']}|@| {job_number}|@| {values['name']}|@| {values['password']}\n")
                # 写入事件日志
                with open(event_log_path, 'a', encoding='utf-8') as file:
                    file.write(f'修改员工|@| {verify_result[0]}|@| {verify_result[1]}|@| 修改员工姓名: {employee_name}，修改员工工号：{self.selected_employee_job_number}|@| {datetime.datetime.now()}\n')
                # 提示修改成功
                messagebox.showinfo("提示", "修改成功")
                # 刷新页面
                self.show_employee_list()
                # 解除禁止操作主界面
                self.root.attributes("-disabled", False)
                # 聚焦到主窗口
                self.root.focus_force()
        
            # 修改物品弹窗关闭事件
            def on_closing_dialog_modify_employee():
                print("关闭修改弹窗")
                self.root.attributes("-disabled", False)
                # 聚焦到主窗口
                self.root.focus_force()
                self.dialog_modify_employee.destroy()

            # 检查是否选中员工
            if self.selected_employee_job_number is None:
                messagebox.showerror("错误", "请选择员工")
                return
            # 弹出员工验证对话框
            verify_result = verify_user_ui(self.root)
            if not verify_result:
                return
            # 获取员工信息
            employee_id, employee_name, employee_password = self.employee[self.selected_employee_job_number]['id'], self.employee[self.selected_employee_job_number]['name'], self.employee[self.selected_employee_job_number]['password']
            print('修改员工:', employee_name, employee_password)

            # 弹出修改员工对话框
            self.dialog_modify_employee = tk.Toplevel(self.employee_frame)
            self.dialog_modify_employee.title("修改员工")
            # self.dialog_modify_employee.geometry("300x150")
            # 配置对话框的列宽权重，让列可以扩展
            self.dialog_modify_employee.grid_columnconfigure(0, weight=1)
            self.dialog_modify_employee.grid_columnconfigure(1, weight=1)
            # 设置关闭事件
            self.dialog_modify_employee.protocol("WM_DELETE_WINDOW", on_closing_dialog_modify_employee)
            # 置于root顶
            self.dialog_modify_employee.transient(self.root)
            # 禁止操作主界面
            self.root.attributes("-disabled", True)
            # 在屏幕中央显示
            x = (self.screen_width - 300) // 2
            y = (self.screen_height - 150) // 2
            self.dialog_modify_employee.geometry(f"300x150+{x}+{y}")
            # 物品名称
            tk.Label(self.dialog_modify_employee, text="员工姓名:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
            user_name_entry = tk.Entry(self.dialog_modify_employee)
            user_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
            user_name_entry.config(width=10)
            user_name_entry.insert(0, employee_name)

            # 第二行添加密码
            tk.Label(self.dialog_modify_employee, text="员工密码:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
            user_pw_entry = tk.Entry(self.dialog_modify_employee, show='*')
            user_pw_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
            user_pw_entry.config(width=10)
            user_pw_entry.insert(0, employee_password)

            # 第三行加入空白标签
            tk.Label(self.dialog_modify_employee, text="").grid(row=2, column=0, columnspan=2)

            # 添加按钮
            tk.Button(self.dialog_modify_employee, text="修改", height=2, width=5, command=lambda: category_modify_commit_employee_event(user_name_entry.get(), user_pw_entry.get(), verify_result)).grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        tk.Label(self.main_frame, text="员工列表页面").pack()
        # # 添加员工列表的具体实现
        # 添加一个新的employeeFrame主页面
        # 定义状态变量，选中的员工id
        self.selected_employee_job_number = None
        

        # 添加一个新的employeeFrame主页面
        self.employee_frame = tk.Frame(self.main_frame)
        self.employee_frame.pack(fill=tk.BOTH, expand=True)
        # # 设置测试背景颜色
        # self.employee_frame.config(bg='red')
        # # 设置测试背景颜色
        # self.employee_frame.config(bg='red')

        # 添加两个frame
        self.left_frame_employee = tk.Frame(self.employee_frame, width=400)
        self.left_frame_employee.pack(side=tk.LEFT, padx=(40,0), fill=tk.Y)
        self.right_frame_employee = tk.Frame(self.employee_frame, width=260)
        self.right_frame_employee.pack(side=tk.RIGHT, padx=(0,40), fill=tk.Y)

        # 左侧frame加入view和滑轮
        self.canvas_employee = tk.Canvas(self.left_frame_employee)
        columns = {"":60, "员工工号":190,"员工姓名":190}
        # 隐藏第一列（“员工工号”）  
        self.tree_employee = ttk.Treeview(self.canvas_employee, columns=list(columns), show='headings')
        self.tree_employee.column("员工工号", width=0, stretch=tk.NO)  
        self.scrollbar_employee = tk.Scrollbar(self.left_frame_employee, orient='vertical')
        for text, width in columns.items():  # 批量设置列属性
            self.tree_employee.heading(text, text=text, anchor='center')
            self.tree_employee.column(text, anchor='center', width=width, stretch=True)  # stretch 不自动拉伸
        self.tree_employee.pack(fill=tk.BOTH, expand=True)
        self.canvas_employee.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) 
        self.scrollbar_employee.pack(side=tk.RIGHT, fill='y')

        # 绑定tree和Scrollbar
        self.scrollbar_employee.configure(command=self.tree_employee.yview)
        self.tree_employee.configure(yscrollcommand=self.scrollbar_employee.set)

        # 绑定tree的单击事件
        self.tree_employee.bind('<Button-1>', on_click_employee)
        # # 绑定tree的双击事件
        # self.tree_employee.bind('<Double-1>', on_click_double_employee)

        # 获取库存数据
        self.employee = load_users()    # 是一个字典
        for index, (job_number,value) in enumerate(self.employee.items(), start=1):
            # self.tree_employee.insert('', 'end', values=(job_number, value['name']))
            self.tree_employee.insert('', 'end',text=value['id'], values=(index, job_number, value['name']))

        # # 往tree中插入数据,备注只显示部分
        # for row in self.employee:
        #     self.tree_employee.insert('', 'end', values=(row[0], row[3][:5]+'...'))

        # 右侧frame加入标签按钮,按钮宽120，高35
        self.label_employee = tk.Label(self.right_frame_employee, text="操作按钮", width=20, height=2, font=("Arial", 15, "bold")).pack(side=tk.TOP)
        tk.Button(self.right_frame_employee, text="添加员工", command=add_employee_event, width=20, height=2).pack(side=tk.TOP, pady=(80,30))
        tk.Button(self.right_frame_employee, text="删除员工", command=remove_employee_event, width=20, height=2).pack(side=tk.TOP, pady=30)
        tk.Button(self.right_frame_employee, text="员工信息修改", command=modify_employee_event, width=20, height=2).pack(side=tk.TOP, pady=30)



    # 创建库存统计页面
    def create_inventory_report(self):
        # 下拉框选中事件
        def on_select(event):
            # 取消全选状态，光标移到文本末尾
            self.combobox.selection_clear()
            # self.combobox.icursor(tk.END)  # 将光标移动到文本框末尾
        
        # 获取选中物品的出库入库记录,四种情况：今日，本周，本月，全部
        def get_current_item_data(item_id, type='today'):
            # 获取时间范围
            def get_time_range(period):
                now = datetime.datetime.now()
                
                if period == "today":
                    start = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
                    end = start + datetime.timedelta(days=1)
                elif period == "week":
                    start = now - datetime.timedelta(days=now.weekday())
                    start = datetime.datetime(start.year, start.month, start.day, 0, 0, 0)
                    end = start + datetime.timedelta(days=7)
                elif period == "month":
                    start = datetime.datetime(now.year, now.month, 1, 0, 0, 0)
                    if now.month == 12:
                        end = datetime.datetime(now.year + 1, 1, 1, 0, 0, 0)
                    else:
                        end = datetime.datetime(now.year, now.month + 1, 1, 0, 0, 0)
                else:
                    raise ValueError("时间段无效")
                
                print('时间范围:', start, end)
                return start, end

            # 筛选数据
            def filter_records(records, period):
                start, end = get_time_range(period)
                return [record for record in records if start <= record[5] < end]  # 修改为按列表索引筛选

            current_item_all = get_current_item(item_id)
            # print('当前物品所有记录:', current_item_all)

            records = current_item_all
            for record in records:
                record[5] = datetime.datetime.strptime(record[5], "%Y-%m-%d %H:%M:%S.%f")  # 转为datetime

            # 返回筛选后的记录
            if type in ['today', 'week', 'month']:
                return filter_records(records, type)
            else:
                return records  # 全部返回
                
        # 获取起始日期的库存统计,进货，销售
        def get_start_date_info(start,end,records):
            
            


        # tk.Label(self.main_frame, text="库存统计页面").pack()
        # 选中物品的id
        self.selected_report_item = None
        # 添加库存统计的具体实现
        # 上下两个frame
        self.top_frame_report = tk.Frame(self.main_frame, height=40)
        self.top_frame_report.pack(fill=tk.X, expand=False)
        # # 设置测试背景颜色
        self.top_frame_report.config(bg='red')
        self.bottom_frame_report = tk.Frame(self.main_frame)
        self.bottom_frame_report.pack(fill=tk.BOTH, expand=True)
        # # # 设置测试背景颜色
        # self.bottom_frame_report.config(bg='blue')

        # 上侧frame加入标签按钮,按钮宽95，高30
        tk.Label(self.top_frame_report, text="当前物品：", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=20)
        # 添加下拉框
        # 获取库存数据
        self.kucun = load_kucun()
        # 获取物品名称
        item_names = [item[0] for item in self.kucun]
        # 默认选中第一个
        self.selected_item = tk.StringVar()
        self.selected_item.set(item_names[0])
        self.selected_report_item = self.kucun[0][1]
        print('当前选中物品id:', self.selected_report_item)

        # 创建下拉框
        self.combobox = ttk.Combobox(self.top_frame_report, font=("Arial", 12, "bold"), textvariable=self.selected_item, width=15, state='readonly')
        self.combobox['values'] = item_names
        self.combobox.pack(side=tk.LEFT, padx=10)
        # 绑定选中事件
        self.combobox.bind("<<ComboboxSelected>>", on_select)

        # 添加三个按钮，今日，本周，本月
        tk.Button(self.top_frame_report, text="本月", font=("Arial", 12, "bold"),width=8, height=1).pack(side=tk.RIGHT, padx=10)
        tk.Button(self.top_frame_report, text="本周", font=("Arial", 12, "bold"),width=8, height=1).pack(side=tk.RIGHT, padx=10)
        tk.Button(self.top_frame_report, text="今日", font=("Arial", 12, "bold"),width=8, height=1).pack(side=tk.RIGHT, padx=10)
        
        # 在上方添加frame
        self.top_frame_report_report = tk.Frame(self.bottom_frame_report, height=35)
        self.top_frame_report_report.pack(side=tk.TOP, fill=tk.X, expand=False)
        # # 设置测试背景颜色
        self.top_frame_report_report.config(bg='black')
        # 下侧frame加入左右两个frame
        self.left_frame_report = tk.Frame(self.bottom_frame_report, width=500)
        self.left_frame_report.pack(side=tk.LEFT, padx=(20,0), fill=tk.Y)
        # # 设置测试背景颜色
        self.left_frame_report.config(bg='yellow')
        self.right_frame_report = tk.Frame(self.bottom_frame_report)
        self.right_frame_report.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        # # 设置测试背景颜色
        self.right_frame_report.config(bg='green')

        # 添加顶部frame的标签
        self.top_time_label = tk.Label(self.top_frame_report_report, text="当前时间范围：xxxxxxxxxx", font=("Arial", 12, "bold"))
        self.top_time_label.pack(side=tk.LEFT, padx=120)

        # 左侧frame加入view和滑轮
        self.canvas_report = tk.Canvas(self.left_frame_report)
        columns = {"类型":100, "数量":100,"余量":100,"时间":200}
        self.tree_report = ttk.Treeview(self.canvas_report, columns=list(columns), show='headings')
        self.scrollbar_report = tk.Scrollbar(self.left_frame_report, orient='vertical')
        for text, width in columns.items():
            self.tree_report.heading(text, text=text, anchor='center')
            self.tree_report.column(text, anchor='center', width=width, stretch=True)  # stretch 不自动拉伸
        self.tree_report.pack(fill=tk.BOTH, expand=True)
        self.canvas_report.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar_report.pack(side=tk.RIGHT, fill='y')
        self.scrollbar_report.configure(command=self.tree_report.yview)
        self.tree_report.configure(yscrollcommand=self.scrollbar_report.set)

        # 默认为第一个物品的当天数据
        # 获取当天的库存数据
        current_item_data = get_current_item_data(self.selected_report_item, 'week')
        print('当前物品当天数据:', current_item_data)
        if current_item_data:
            for row in current_item_data:
                if row[0] == 'add':
                    set_type = '进货'
                else:
                    set_type = '销售'
                self.tree_report.insert('', 'end', values=(set_type, row[1], row[2], row[5].strftime("%Y-%m-%d %H:%M:%S")))
        else:
            self.tree_report.insert('', 'end', values=('无数据', '无数据', '无数据', '无数据'))
        # 设置标签文字
        self.top_time_label.config(text=f"当前时间范围：{datetime.datetime.now().strftime('%Y-%m-%d')}")

        # 右侧frame加入三个frame，分别是库存统计，进货统计，销售统计
        self.top_frame_right_report = tk.Frame(self.right_frame_report, height=100)
        self.top_frame_right_report.pack(side=tk.TOP, fill=tk.X, expand=1)
        
        self.middle_frame_right_report = tk.Frame(self.right_frame_report, height=100)
        self.middle_frame_right_report.pack(side=tk.TOP, fill=tk.X, expand=1)

        self.bottom_frame_right_report = tk.Frame(self.right_frame_report, height=100)
        self.bottom_frame_right_report.pack(side=tk.TOP, fill=tk.X, expand=1)

        # 添加三个标签按钮
        self.top_frame_right_report_label = tk.Label(self.top_frame_right_report, text="库存统计", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=20)
        self.middle_frame_right_report_label = tk.Label(self.middle_frame_right_report, text="进货统计", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=20)
        self.bottom_frame_right_report_label = tk.Label(self.bottom_frame_right_report, text="销售统计", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=20)

        

    
    # 添加物品事件
    def add_item_event(self):
        # 弹出添加物品对话框
        self.dialog_add_item_category = tk.Toplevel(self.category_frame)
        self.dialog_add_item_category.title("添加物品")
        self.dialog_add_item_category.geometry("300x150")
        # 配置对话框的列宽权重，让列可以扩展
        self.dialog_add_item_category.grid_columnconfigure(0, weight=1)
        self.dialog_add_item_category.grid_columnconfigure(1, weight=1)
        # 设置关闭事件
        self.dialog_add_item_category.protocol("WM_DELETE_WINDOW", self.on_closing_dialog_add_item_category)
        # 置于root顶
        self.dialog_add_item_category.transient(self.root)
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


    # 提交添加物品事件
    def category_add_commit_item_event(self, item_name, item_quantity, comment_text): 
        # 验证逻辑是否合法
        # 1、验证物品名称是否为空
        if not item_name:
            messagebox.showerror("错误", "请输入物品名称")
            # 聚焦到弹窗
            self.dialog_add_item_category.focus_force()
            return False
        # 2、验证quantitym是否为数字
        if not item_quantity.isdigit():
            messagebox.showerror("错误", "请输入数字")
            # 聚焦到弹窗
            self.dialog_add_item_category.focus_force()
            return False
        # 3、验证quantitym是否大于0
        if int(item_quantity) < 0:
            messagebox.showerror("错误", "请输入大于等于0的数字")
            # 聚焦到弹窗
            self.dialog_add_item_category.focus_force()
            return False
        
        # 验证操作人员，验证通过才能进行操作
        verify_result = verify_user_ui(self.dialog_add_item_category)
        if not verify_result:
            return
        # 生成唯一ID
        id = generate_id('item')
        print('添加物品:', item_name, id, item_quantity, comment_text)
        # 生成 
        # 去掉备注中的换行符
        comment_text = comment_text.replace('\n', '  ')
        # 写入库存文件
        with open(kucun_path, 'a', encoding='utf-8') as file:
            file.write(f"{item_name}|@|{id}|@|{item_quantity}|@|{comment_text}\n")
        # 写入库存修改日志
        with open(modify_inventory_log_path, 'a', encoding='utf-8') as file:
            file.write(f'{item_name}|@| add|@| {item_quantity}|@| {item_quantity}|@| {verify_result[1]}|@| {verify_result[0]}|@| {datetime.datetime.now()}\n')
        # 写入事件日志
        with open(event_log_path, 'a', encoding='utf-8') as file:
            file.write(f'添加新物品|@| {verify_result[0]}|@| {verify_result[1]}|@| 货物: {item_name}, 数量: {item_quantity}|@| {datetime.datetime.now()}\n')
        # 创建物品表格文件->id.txt【修改类型|@| 修改数量|@| 修改后数量|@| 操作员工姓名|@| 操作员工ID|@| 修改时间  】,在items文件夹下
        with open(f'{items_folder_path}{id}.txt', 'w', encoding='utf-8') as file:
            file.write("修改类型|@| 修改数量|@| 修改后数量|@| 操作员工姓名|@| 操作员工ID|@| 修改时间\n")
            file.write(f"create|@| {item_quantity}|@| {item_quantity}|@| {verify_result[0]}|@| {verify_result[1]}|@| {datetime.datetime.now()}\n")
        # 提示添加成功
        messagebox.showinfo("提示", "添加成功")
        # 刷新页面
        self.show_category_management()
        # 解除禁止操作主界面
        self.root.attributes("-disabled", False)
        # 聚焦到主窗口
        self.root.focus_force()
    
    # 提交物品弹窗关闭事件
    def on_closing_dialog_add_item_category(self):
        print("关闭提交弹窗")
        self.root.attributes("-disabled", False)
        # 聚焦到主窗口
        self.root.focus_force()
        self.dialog_add_item_category.destroy()
    
    # 删除物品事件
    def remove_item_event(self):
        # 检查是否选中物品
        if self.selected_item_index is None:
            messagebox.showerror("错误", "请选择物品")
            return
        # 弹出员工验证对话框
        verify_result = verify_user_ui(self.root)
        if not verify_result:
            return
        # 获取物品信息
        item_name, item_id, item_quantity, item_comment = self.kucun[self.selected_item_index]
        print('要删除的物品信息:', item_name, item_id, item_quantity, item_comment)

        # 读取库存文件
        self.kucun = load_kucun()
        # 删除物品
        self.kucun.pop(self.selected_item_index)
        # 写入文件
        with open(kucun_path, 'w', encoding='utf-8') as file:
            file.write("name|@| id|@| num|@| command\n")
            for row in self.kucun:
                # file.write(f"{row[0]}|@|{row[1]}|@|{row[2]}\n")
                w_str = ""+row[0]
                for i in range(1,len(row)):
                    w_str += "|@|"+row[i]
                file.write(w_str+"\n")
        # 写入库存修改日志
        with open(modify_inventory_log_path, 'a', encoding='utf-8') as file:
            file.write(f'{item_name}|@| remove|@| {item_quantity}|@| 0|@| {verify_result[1]}|@| {verify_result[0]}|@| {datetime.datetime.now()}\n')
        # 写入事件日志
        with open(event_log_path, 'a', encoding='utf-8') as file:
            file.write(f'删除物品|@| {verify_result[0]}|@| {verify_result[1]}|@| 货物: {item_name}, 数量: {item_quantity}|@| {datetime.datetime.now()}\n')
        # 删除物品表格文件
        os.remove(f'{items_folder_path}{item_id}.txt')
        # 提示删除成功
        messagebox.showinfo("提示", "删除成功")
        # 聚焦到主窗口
        self.root.focus_force()
        # 刷新页面
        self.show_category_management()

    
    # 修改物品事件
    def modify_item_event(self):
        # 提交修改物品事件
        def category_modify_commit_item_event(self, item_name_entry, comment_text): 
            # 原来物品信息
            item_name, item_id, item_quantity, item_comment = self.kucun[self.selected_item_index]
            print('修改后物品:', item_name_entry, item_id, item_quantity, comment_text)

            # 修改物品信息
            self.kucun[self.selected_item_index] = [item_name_entry, item_id, item_quantity, comment_text]

            # 写入库存文件
            with open(kucun_path, 'w', encoding='utf-8') as file:
                file.write("name|@| id|@| num|@| command\n")
                for row in self.kucun:
                    # file.write(f"{row[0]}|@|{row[1]}|@|{row[2]}\n")
                    w_str = ""+row[0]
                    for i in range(1,len(row)):
                        w_str += "|@|"+row[i]
                    file.write(w_str+"\n")
            ########################################################->明天修改
            # 不用写入库存修改，因为库存数量没有改变，需要修改库存记录名称，单独开表
            # # 写入库存修改日志
            # with open(modify_inventory_log_path, 'a', encoding='utf-8') as file:
            #     file.write(f'{item_name}|@| modify|@| {item_quantity}|@| {item_quantity}|@| {verify_result[1]}|@| {verify_result[0]}|@| {datetime.datetime.now()}\n')
            # 写入事件日志
            with open(event_log_path, 'a', encoding='utf-8') as file:
                file.write(f'修改物品信息|@| {verify_result[0]}|@| {verify_result[1]}|@| 货物: {item_name}, 备注: {item_comment}；修改为： 货物：{item_name_entry}，备注：{comment_text}|@| {datetime.datetime.now()}\n')
            # 提示修改成功
            messagebox.showinfo("提示", "修改成功")
            # 刷新页面
            self.show_category_management()
            # 解除禁止操作主界面
            self.root.attributes("-disabled", False)
            # 聚焦到主窗口
            self.root.focus_force()
    
        # 修改物品弹窗关闭事件
        def on_closing_dialog_modify_item_category():
            print("关闭提交弹窗")
            self.root.attributes("-disabled", False)
            # 聚焦到主窗口
            self.root.focus_force()
            self.dialog_modify_item_category.destroy()

        # 检查是否选中物品
        if self.selected_item_index is None:
            messagebox.showerror("错误", "请选择物品")
            return
        # 弹出员工验证对话框
        verify_result = verify_user_ui(self.root)
        if not verify_result:
            return
        # 获取物品信息
        item_name, item_id, item_quantity, item_comment = self.kucun[self.selected_item_index]
        print('修改物品:', item_name, item_id, item_quantity, item_comment)

        # 弹出修改物品对话框
        self.dialog_modify_item_category = tk.Toplevel(self.category_frame)
        self.dialog_modify_item_category.title("修改物品")
        self.dialog_modify_item_category.geometry("300x150")
        # 配置对话框的列宽权重，让列可以扩展
        self.dialog_modify_item_category.grid_columnconfigure(0, weight=1)
        self.dialog_modify_item_category.grid_columnconfigure(1, weight=1)
        # 设置关闭事件
        self.dialog_modify_item_category.protocol("WM_DELETE_WINDOW", on_closing_dialog_modify_item_category)
        # 置于root顶
        self.dialog_modify_item_category.transient(self.root)
        # 禁止操作主界面
        self.root.attributes("-disabled", True)
        # 在屏幕中央显示
        x = (self.screen_width - 420) // 2
        y = (self.screen_height - 250) // 2
        self.dialog_modify_item_category.geometry(f"420x250+{x}+{y}")
        # 物品名称
        tk.Label(self.dialog_modify_item_category, text="物品名称:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        item_name_entry = tk.Entry(self.dialog_modify_item_category)
        item_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        item_name_entry.config(width=10)
        item_name_entry.insert(0, item_name)

        # 第二行添加备注
        tk.Label(self.dialog_modify_item_category, text="备注：").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        # 添加备注框
        comment_quantity = tk.Text(self.dialog_modify_item_category, width=27, height=8)
        comment_quantity.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        # 添加默认值
        comment_quantity.insert(tk.END, item_comment)

        # 第三行加入空白标签
        tk.Label(self.dialog_modify_item_category, text="").grid(row=2, column=0, columnspan=2)

        # 添加按钮
        tk.Button(self.dialog_modify_item_category, text="修改", height=2, width=5, command=lambda: category_modify_commit_item_event(self, item_name_entry.get(), comment_quantity.get("1.0", "end-1c"))).grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    
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