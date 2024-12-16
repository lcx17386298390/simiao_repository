import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import datetime

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
def add_item(item_name, quantity):
    with open(f'{item_name}.txt', 'a') as file:
        file.write(f'{datetime.datetime.now()}, +{quantity}\n')

def remove_item(item_name, quantity):
    with open(f'{item_name}.txt', 'a') as file:
        file.write(f'{datetime.datetime.now()}, -{quantity}\n')

def modify_item(item_name, quantity):
    with open(f'{item_name}.txt', 'a') as file:
        file.write(f'{datetime.datetime.now()}, {quantity}\n')

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
        self.root = root
        self.root.title("寺庙库存管理系统")
        self.root.geometry("800x500")
        
        self.menu_frame = tk.Frame(root)
        self.menu_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.buttons = {}
        self.create_main_menu()

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
    
    def show_inventory_management(self):
        self.clear_frame()
        self.highlight_button('inventory')
        self.create_inventory_management()
    
    def show_category_management(self):
        self.clear_frame()
        self.highlight_button('category')
        self.create_category_management()
    
    def show_employee_list(self):
        self.clear_frame()
        self.highlight_button('employee')
        self.create_employee_list()
    
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
    
    def create_inventory_management(self):

        left_frame = tk.Frame(self.main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        right_frame = tk.Frame(self.main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(left_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 库存类别列表
        self.category_listbox = tk.Listbox(left_frame, yscrollcommand=scrollbar.set)
        self.category_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.category_listbox.yview)
        # 设置宽度 
        self.category_listbox.config(width=10)
        # # 设置宽度可以界面左右拉动
        # self.category_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 示例库存类别
        categories = ["类别1", "类别2", "类别3", "类别4", "类别5", "类别6", "类别7", "类别8", "类别9", "类别10", "类别11", "类别12", "类别13", "类别14", "类别15",
                        "类别16", "类别17", "类别18", "类别19", "类别20", "类别21", "类别22", "类别23", "类别24", "类别25", "类别26", "类别27", "类别28", "类别29", "类别30"]
        for category in categories:
            self.category_listbox.insert(tk.END, category)
        
        self.category_listbox.bind("<<ListboxSelect>>", self.show_inventory_items)
        
        self.inventory_frame = right_frame
    
    def show_inventory_items(self, event):
        selected_category = self.category_listbox.get(self.category_listbox.curselection())
        self.clear_inventory_frame()
        
        tk.Label(self.inventory_frame, text=f"{selected_category}的库存物品").grid(row=0, column=0, columnspan=2)
    
    def clear_inventory_frame(self):
        for widget in self.inventory_frame.winfo_children():
            widget.destroy()
    
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
        
        tk.Button(self.category_frame, text="添加", command=self.add_item).grid(row=3, column=0)
        tk.Button(self.category_frame, text="删除", command=self.remove_item).grid(row=3, column=1)
        tk.Button(self.category_frame, text="修改", command=self.modify_item).grid(row=3, column=2)
        
        tk.Button(self.category_frame, text="生成日报表", command=self.generate_daily_report).grid(row=4, column=0, columnspan=3)
    
    def create_employee_list(self):
        tk.Label(self.main_frame, text="员工列表页面").pack()
        # 添加员工列表的具体实现

    def create_inventory_report(self):
        tk.Label(self.main_frame, text="库存统计页面").pack()
        # 添加库存统计的具体实现
    
    def add_item(self):
        if self.verify_user():
            item_name = self.item_name.get()
            quantity = int(self.item_quantity.get())
            add_item(item_name, quantity)
            messagebox.showinfo("成功", "添加成功")
    
    def remove_item(self):
        if self.verify_user():
            item_name = self.item_name.get()
            quantity = int(self.item_quantity.get())
            remove_item(item_name, quantity)
            messagebox.showinfo("成功", "删除成功")
    
    def modify_item(self):
        if self.verify_user():
            item_name = self.item_name.get()
            quantity = int(self.item_quantity.get())
            modify_item(item_name, quantity)
            messagebox.showinfo("成功", "修改成功")
    
    def generate_daily_report(self):
        if self.verify_user():
            item_name = self.item_name.get()
            report = generate_report(item_name, 'daily')
            report_str = "\n".join([f"{key}: {value}" for key, value in report.items()])
            messagebox.showinfo("日报表", report_str)
    
    def verify_user(self):
        dialog = VerifyDialog(self.root, title="验证")
        dialog.geometry("300x150")
        user_id, password = dialog.get_credentials()
        
        if verify_user(user_id, password):
            return True
        else:
            messagebox.showerror("错误", "用户验证失败")
            return False

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()