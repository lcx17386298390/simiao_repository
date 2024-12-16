import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import datetime
from tkinter import ttk

# 用户管理
def load_users():
    users = {}
    if os.path.exists('users.txt'):
        with open('users.txt', 'r') as file:
            for line in file:
                name, id, password = line.strip().split(',')
                users[id] = {'name': name, 'password': password}
    return users

def verify_user(id, password):
    users = load_users()
    if id in users and users[id]['password'] == password:
        return True
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
def modify_item(item_name, quantity, type='add', index=0):
    if type == 'add':
        # 1、操作库存数量文件
        # 先读取文件，再写入
        lines = []
        with open(f'files/kucun.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        data = [line.strip().split(',') for line in lines[1:]]
        # # 修正格式代码
        # data = []
        # for i in range(1, len(lines)):
        #     data.append(lines[i].split(','))
        #     print(data[0])
        #     for j in range(len(data[i-1])):
        #         data[i-1][j] = data[i-1][j].strip()
        # print(data)
        # 修改库存数量
        data[index][2] = ' ' + str(int(data[index][2]) + int(quantity))
        # 写入文件
        with open(f'files/kucun.txt', 'w', encoding='utf-8') as file:
            file.write("name, id, num\n")
            for row in data:
                file.write(f"{row[0]},{row[1]},{row[2]}\n")
        # 2、对此次操作进行记录
        
    else:
        with open(f'{item_name}.txt', 'a') as file:
            file.write(f'{datetime.datetime.now()}, -{quantity}\n')

# 统计功能
def generate_report(item_name, period='daily'):
    with open(f'{item_name}.txt', 'r') as file:
        lines = file.readlines()
    
    report = {}
    for line in lines:
        date_str, change = line.strip().split(', ')
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

# 自定义验证对话框
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

        # 库存
        self.kucun = None

        self.root = root
        self.root.title("寺庙库存管理系统")
        self.root.geometry("800x500")
        
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

        # 读取kucun文件，查看库存物品
        with open('files/kucun.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # headers = lines[0].strip().split(',')
        headers = ['物品名称', '库存数量']
        data = [line.strip().split(',') for line in lines[1:]]
        # 库存更新
        self.kucun = data

        # 创建一个Canvas来容纳Treeview
        canvas = tk.Canvas(self.inventory_frame)
        scrollbar = ttk.Scrollbar(self.inventory_frame, orient='vertical', command=canvas.yview)
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
        for row in data:
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
        self.dialog_inventory.geometry("300x150")
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
        
        # 第四行加入空白标签 (如果需要)
        tk.Label(self.dialog_inventory, text="").grid(row=3, column=0, columnspan=2)
        
        # 添加按钮
        tk.Button(self.dialog_inventory, text="添加", command=lambda: self.add_product(product_name, quantity_entry.get(), selected_index)).grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        
        # 减少按钮
        tk.Button(self.dialog_inventory, text="减少", command=lambda: self.remove_product(product_name, quantity_entry.get(), selected_index)).grid(row=4, column=1, padx=10, pady=10, sticky="ew")
    
    # 添加产品数量,index为选中的行(从0开始),便于后续修改
    def add_product(self, product_name, quantitym, index):
        # 添加产品数量
        modify_item(product_name, quantitym, "add", index)
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
        
    
    # 减少产品数量
    def remove_product(self, product_name, quantity):
        # 减少产品数量
        remove_item(product_name, quantity)
        # 刷新页面
        self.clear_inventory_frame()
        self.create_inventory_management()
    
    # 清空库存物品
    def clear_inventory_frame(self):
        for widget in self.inventory_frame.winfo_children():
            widget.destroy()
    
    # 创建库存类别管理页面
    def create_category_management(self):
        
        # 主页面
        self.category_frame = tk.Frame(self.main_frame)
        self.category_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(self.main_frame, text="库存类别管理页面").pack()

        # 添加库存类别管理的具体实现
        tk.Label(self.category_frame, text="物品名称:").grid(row=1, column=0)
        self.item_name = tk.Entry(self.category_frame)
        self.item_name.grid(row=1, column=1)
        
        tk.Label(self.category_frame, text="数量:").grid(row=2, column=0)
        self.item_quantity = tk.Entry(self.category_frame)
        self.item_quantity.grid(row=2, column=1)
        
        tk.Button(self.category_frame, text="添加", command=self.add_item_event).grid(row=3, column=0)
        tk.Button(self.category_frame, text="删除", command=self.remove_item_event).grid(row=3, column=1)
        tk.Button(self.category_frame, text="修改", command=self.modify_item_event).grid(row=3, column=2)
        
        tk.Button(self.category_frame, text="生成日报表", command=self.generate_daily_report).grid(row=4, column=0, columnspan=3)
    
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
        if self.verify_user():
            item_name = self.item_name.get()
            quantity = int(self.item_quantity.get())
            add_item(item_name, quantity)
            messagebox.showinfo("成功", "添加成功")
    
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
    
    # 验证用户
    def verify_user(self):
        dialog_verify = VerifyDialog(self.root, title="验证")
        dialog_verify.geometry("300x150")
        user_id, password = dialog_verify.get_credentials()
        
        if verify_user(user_id, password):
            return True
        else:
            messagebox.showerror("错误", "用户验证失败")
            return False

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()