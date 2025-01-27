import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import datetime
from tkinter import ttk
import time
import random
import base64
import shutil
from tkcalendar import Calendar

# txt文件路径
kucun_path = 'files/kucun.txt'
event_log_path = 'files/event_log.txt'
modify_inventory_log_path = 'files/modify_inventory_log.txt'
users_path = 'files/users.txt'
items_folder_path = 'files/items/'
user_index_temp_path = 'files/user_index_temp.txt'
icon_path = 'files/icon.ico'

    
# 示例：在每次写入之前进行备份
def write_with_backup(file_path, backup=True):
    # 进行备份操作
    if backup and os.path.exists(file_path):
        # 获取当前日期时间，避免覆盖备份文件
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.replace('.txt', f'_backup.txt')
        # 修改备份文件路径
        backup_path = backup_path.replace('files', 'backup_files')
        # 去除空格
        backup_path = backup_path.replace(' ', '')
        
        # 如果备份文件夹不存在，创建文件夹
        backup_dir = os.path.dirname(backup_path)  # 获取文件所在的目录
        if not os.path.exists(backup_dir):
            os.mkdir(backup_dir)
        # 创建备份文件
        shutil.copy(file_path, backup_path)
        print(f"备份文件已保存：{backup_path}")


# 加密/解密
key = "secret_key"  # 密钥
# 加密
def xor_encrypt_decrypt_line(line, key=key):
    # 使用 XOR 对每个字符进行加密/解密
    encrypted_chars = [chr(ord(char) ^ ord(key[i % len(key)])) for i, char in enumerate(line)]
    # 将加密后的字符列表合并成一个字符串
    encrypted_line = ''.join(encrypted_chars)
    # 对加密后的字符串进行 Base64 编码，保证输出的字符都可以打印
    encoded_line = base64.b64encode(encrypted_line.encode('utf-8')).decode('utf-8')
    return encoded_line

# 解密
# 解密时先进行 Base64 解码，然后再 XOR 操作
def xor_decrypt_line(encrypted_line, key):
    # 对 Base64 编码的数据进行解码
    decoded_line = base64.b64decode(encrypted_line.encode('utf-8')).decode('utf-8')
    # 使用 XOR 进行解密
    decrypted_chars = [chr(ord(char) ^ ord(key[i % len(key)])) for i, char in enumerate(decoded_line)]
    # 将解密后的字符列表合并成一个字符串
    decrypted_line = ''.join(decrypted_chars)
    return decrypted_line

# 生成唯一ID
def generate_id(prefix='ID'):
    return f'{prefix}_{int(time.time())}{random.randint(1000, 9999)}'


# 读取用户文件
def load_users():
    users = {}
    try:
        with open(f'{users_path}', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines[1:]:
                id, job_number, name, password = line.strip().split('|@| ')
                password = xor_decrypt_line(password, key)  # 解密
                users[job_number] = {'id': id, 'name': name, 'password': password}
    except Exception as e:
        messagebox.showerror("错误", f"读取用户文件失败,存储格式错误：{e}")
    finally:
        return users

# 读取库存文件
def load_kucun():
    kucun = []
    try:
        with open(kucun_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines[1:]:
                name, id, price, num, comment = line.strip().split('|@|')
                kucun.append([name, id.replace(' ',''), price, num, comment])
    except Exception as e:
        messagebox.showerror("错误", f"读取库存文件失败,存储格式错误：{e}")
    finally:
        return kucun

# 获取物品的所有出库入库记录
def get_current_item(item_id):
    item_path = items_folder_path + f"{item_id}.txt"
    current_item_record = []
    # 如果没有文件，创建文件
    if not os.path.exists(item_path):
        with open(item_path, 'w', encoding='utf-8') as file:
            file.write("修改类型|@| 修改数量|@| 修改后数量|@| 操作员工姓名|@| 操作员工ID|@| 修改时间|@| 实时价格|@| 售出金额\n")
    try:
        with open(item_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines[1:]:
                record = line.strip().split('|@| ')
                current_item_record.append(record)
    except Exception as e:
        messagebox.showerror("错误", f"读取物品文件失败,存储格式错误：{e}")
    finally:
        return current_item_record

# 获取事件日志
def get_event_log():
    event_log = []
    try:
        with open(event_log_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines[1:]:
                event = line.strip().split('|@| ')
                event_log.append(event)
    except Exception as e:
        messagebox.showerror("错误", f"读取事件日志文件失败,存储格式错误：{e}")
    finally:
        return event_log

# 得到用户下标标记
def get_user_index_temp():
    if os.path.exists(f'{user_index_temp_path}'):
        with open(f'{user_index_temp_path}', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            return int(lines[0].strip())
    return 0

# 保存用户下标标记
def save_user_index_temp(index):
    # 保存前先备份
    write_with_backup(user_index_temp_path)
    with open(f'{user_index_temp_path}', 'w', encoding='utf-8') as file:
        file.write(f'{index}\n')

# 字符串是否是数字，最小值，最大值
def is_price(s):
    try:
        num = float(s)
        if max is not None and num < 0:
            # 提示错误
            messagebox.showerror("错误", "请输入大于0的数字")
            print("请输入大于0的数字")
            return False
        return True
    except ValueError:
        # 提示错误
        messagebox.showerror("错误", "请输入数字")
        print("请输入数字")
        return False


def verify_user(job_number, password):
    users = load_users()

    if job_number in users and users[job_number]['password'].strip() == password:
        return [job_number, users[job_number]['name'].strip()]
    return False


# 验证用户->弹出验证用户信息对话框,成功返回用户信息,失败返回False
def verify_user_ui(parent, level='root', job_number_level=None):
    ########## 测试代码 ##########
    return ['root', '管理员']
    dialog_verify = VerifyDialog(parent,title="验证")
    print("弹出验证用户信息对话框")
    user_id, password = dialog_verify.get_credentials()
    # 有权限工号
    if level == 'self_or_root' and job_number_level :
        if job_number_level != user_id and user_id != 'root':
            messagebox.showerror("错误", "仅本人或管理员用户可以操作")
            return False
    elif level == 'root':
        if user_id != 'root':
            messagebox.showerror("错误", "仅管理员用户可以操作")
            return False
    else:   # all
        pass

    # 返回信息
    verify_result = verify_user(user_id, password)
    if not verify_result:
        messagebox.showerror("错误", "用户验证失败")
        return False
    else:
        # messagebox.showinfo("成功", "用户验证成功")
        print("该用户信息：", verify_result)
        return verify_result


# 修改物品操作 -> 通过此操作进行添加数量和减少数量
def modify_item(myself, item_name, quantity, type='add', index=0, parent=None):
    # 验证操作人员，验证通过才能进行操作
    verify_result = verify_user_ui(parent, level='all')
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
        myself.kucun[index][3] = ' ' + str(int(myself.kucun[index][3]) + int(quantity))
    elif type == 'remove':
        # 修改库存数量
        myself.kucun[index][3] = ' ' + str(int(myself.kucun[index][3]) - int(quantity))
    
    # 先备份文件
    write_with_backup(kucun_path)
    write_with_backup(event_log_path)
    write_with_backup(modify_inventory_log_path)
    write_with_backup(f'{items_folder_path}{myself.kucun[index][1]}.txt')
    # 写入文件
    with open(kucun_path, 'w', encoding='utf-8') as file:
        file.write("name|@| id|@| price|@| num|@| command\n")
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
            file.write(f'进货|@| {verify_result[0]}|@| {verify_result[1]}|@| 货物: {item_name}, 进货量：{quantity},---> 数量从{int(myself.kucun[index][3]) - int(quantity)}修改为{myself.kucun[index][3]}|@| {datetime.datetime.now()}\n')
        with open(f'{modify_inventory_log_path}', 'a', encoding='utf-8') as file:
            # 记录库存变更  （物品名称|@| 修改类型|@| 修改数量|@| 修改后数量|@| 操作员工姓名|@| 操作员工ID|@| 修改时间）
            file.write(f'{item_name}|@| add|@| {quantity}|@| {myself.kucun[index][2]}|@| {verify_result[1]}|@| {verify_result[0]}|@| {datetime.datetime.now()}\n')
        # 修改物品表格文件->id.txt【修改类型|@| 修改数量|@| 修改后数量|@| 操作员工姓名|@| 操作员工ID|@| 修改时间  】（添加不写金额）,在items文件夹下
        with open(f'{items_folder_path}{myself.kucun[index][1]}.txt', 'a', encoding='utf-8') as file:
            file.write(f'add|@| {quantity}|@| {myself.kucun[index][3]}|@| {verify_result[1]}|@| {verify_result[0]}|@| {datetime.datetime.now()}\n')

            
    elif type == 'remove':
        # 2、对此次操作进行记录，记录到事件操作表和修改库存表
        with open(f'{event_log_path}', 'a', encoding='utf-8') as file:
            # 记录事件操作  （事件描述, 操作员工id, 操作员工, 变更内容, 操作时间）
            file.write(f'售出|@| {verify_result[0]}|@| {verify_result[1]}|@| 货物: {item_name}, 进货量：{quantity},---> 数量从{int(myself.kucun[index][3]) + int(quantity)}修改为{myself.kucun[index][3]}|@| {datetime.datetime.now()}\n')
        with open(f'{modify_inventory_log_path}', 'a', encoding='utf-8') as file:
            # 记录库存变更  （物品名称|@| 修改类型|@| 修改数量|@| 修改后数量|@| 操作员工姓名|@| 操作员工ID|@| 修改时间）
            file.write(f'{item_name}|@| remove|@| {quantity}|@| {myself.kucun[index][2]}|@| {verify_result[1]}|@| {verify_result[0]}|@| {datetime.datetime.now()}\n')
        # 修改物品表格文件->id.txt【修改类型|@| 修改数量|@| 修改后数量|@| 操作员工姓名|@| 操作员工ID|@| 修改时间  】,在items文件夹下
        # 记录当时的价格和计算卖出的金额
        temp_price = myself.kucun[index][2]
        sell_price = int(quantity) * float(temp_price)
        with open(f'{items_folder_path}{myself.kucun[index][1]}.txt', 'a', encoding='utf-8') as file:
            # file.write(f'remove|@| {quantity}|@| {myself.kucun[index][3]}|@| {verify_result[1]}|@| {verify_result[0]}|@| {datetime.datetime.now()}\n')
            file.write(f'remove|@| {quantity}|@| {myself.kucun[index][3]}|@| {verify_result[1]}|@| {verify_result[0]}|@| {datetime.datetime.now()}|@| {temp_price}|@| {sell_price}\n')
    messagebox.showinfo("成功", "操作成功")
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

        # # 测试添加默认值
        # self.user_id_entry.insert(0, "root")
        # self.password_entry.insert(0, "1234")
        
        return self.user_id_entry
    
    def apply(self):
        self.user_id = self.user_id_entry.get()
        self.password = self.password_entry.get()
    
    def get_credentials(self):
        if self.user_id and self.password:
            return self.user_id, self.password
        return None, None
    
    # 取消按钮事件，关闭窗口
    def cancel(self, event=None):
        print("取消按钮")
        self.parent.focus_set()
        self.destroy()

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
        # 设置图标
        self.root.iconbitmap(icon_path)
        
        self.menu_frame = tk.Frame(root)
        self.menu_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.buttons = {}
        self.report_buttons = {}
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
        # 事件日志
        self.buttons['event_log'] = tk.Button(self.menu_frame, text="事件日志", command=self.show_event_log, font=button_font)
        self.buttons['event_log'].pack(side=tk.LEFT)
    
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
    
    # 显示事件日志页面
    def show_event_log(self):
        self.clear_frame()
        self.highlight_button('event_log')
        self.create_event_log()
    
    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def highlight_button(self, button_key):
        for key, button in self.buttons.items():
            if key == button_key:
                button.config(bg='lightblue')
            else:
                button.config(bg='SystemButtonFace')
    def highlight_report_button(self, button_key):
        for key, button in self.report_buttons.items():
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
        headers = ['','物品名称', '价格', '库存数量']
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
            self.tree_inventory.insert('', 'end', values=(index+1,row[0], row[2], row[3]))
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
        product_price = float(item_values[2])  # 产品价格
        product_quantity = int(item_values[3])  # 库存数量

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

        # 显示价格
        tk.Label(self.dialog_inventory, text="价格:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        tk.Label(self.dialog_inventory, text=product_price).grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # 显示库存数量
        tk.Label(self.dialog_inventory, text="库存数量:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        tk.Label(self.dialog_inventory, text=product_quantity).grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # 输入操作数量
        tk.Label(self.dialog_inventory, text="库存操作数量:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        quantity_entry = tk.Entry(self.dialog_inventory)
        quantity_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        quantity_entry.config(width=10)
        # 默认值为1
        quantity_entry.insert(0, "1")
        # 只能输入数字

        # 离开焦点事件
        # quantity_entry.bind('<FocusOut>',lambda e: self.on_focus_out_inventory_event(product_quantity, e))
        
        # 第四行加入空白标签 (如果需要)
        tk.Label(self.dialog_inventory, text="").grid(row=3, column=0, columnspan=2)
        
        # 添加按钮
        tk.Button(self.dialog_inventory, text="进货", command=lambda: self.add_product(product_name, product_quantity, quantity_entry.get(), selected_index)).grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        
        # 减少按钮
        tk.Button(self.dialog_inventory, text="售出", command=lambda: self.remove_product(product_name, product_quantity, quantity_entry.get(), selected_index)).grid(row=4, column=1, padx=10, pady=10, sticky="ew")
    
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
            self.tree_category.insert('', 'end', values=(index, row[0], row[4][:5]+'...'))

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
        self.dialog_category.geometry(f"300x190+{x}+{y}")
        # # 设置关闭事件
        # self.dialog_category.protocol("WM_DELETE_WINDOW", self.on_closing_dialog_category)
        # 聚焦到弹窗
        self.dialog_category.focus_force()
        # 显示产品名称
        tk.Label(self.dialog_category, text="产品名称:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        tk.Label(self.dialog_category, text=item_data[1]).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        # 显示价格
        tk.Label(self.dialog_category, text="价格:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        tk.Label(self.dialog_category, text=self.kucun[self.selected_item_index][2]).grid(row=1, column=1, padx=10, pady=5, sticky="w")
        # 显示完整备注，使用文字框，不可编辑
        tk.Label(self.dialog_category, text="备注:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        text = tk.Text(self.dialog_category, width=27, height=8)
        text.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        # 显示完整备注
        text.insert(tk.END, self.kucun[self.selected_item_index][4])
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
            self.selected_employee_job_number = item_data[1]
            
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
            verify_result = verify_user_ui(self.root, level='root')
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
            # 备份文件
            write_with_backup(users_path)
            write_with_backup(event_log_path)

            # 添加用户
            with open(users_path, 'a', encoding='utf-8') as file:
                # 加密密码
                password_secret = xor_encrypt_decrypt_line(employee_password)
                file.write(f"{employee_id}|@| {employee_job_number}|@| {employee_name}|@| {password_secret}\n")# id|@| job_number|@| name|@| password
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
            verify_result = verify_user_ui(self.root, level='root')
            if not verify_result:
                return
            # 获取员工信息
            employee_id, employee_name, employee_password = self.employee[self.selected_employee_job_number]['id'], self.employee[self.selected_employee_job_number]['name'], self.employee[self.selected_employee_job_number]['password']
            print('删除员工:', employee_name, employee_password)
            # 删除员工
            self.employee.pop(self.selected_employee_job_number)
            # 备份文件
            write_with_backup(users_path)
            write_with_backup(event_log_path)
            # 写入员工文件
            with open(users_path, 'w', encoding='utf-8') as file:
                # 写入表头
                file.write("id|@| job_number|@| name|@| password\n")
                # 重新写入员工文件
                for job_number, values in self.employee.items():
                    password_secret = xor_encrypt_decrypt_line(values['password'])
                    file.write(f"{values['id']}|@| {job_number}|@| {values['name']}|@| {password_secret}\n")
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

                # 备份文件
                write_with_backup(users_path)
                write_with_backup(event_log_path)
                # 写入用户文件
                with open(users_path, 'w', encoding='utf-8') as file:
                    # 写入表头
                    file.write("id|@| job_number|@| name|@| password\n")
                    # 重新写入员工文件
                    for job_number, values in self.employee.items():
                        # 加密密码
                        password_secret = xor_encrypt_decrypt_line(values['password'])
                        file.write(f"{values['id']}|@| {job_number}|@| {values['name']}|@| {password_secret}\n")
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
            print('选中员工:', self.selected_employee_job_number)
            # 弹出员工验证对话框
            verify_result = verify_user_ui(self.root, level='self_or_root', job_number_level=self.selected_employee_job_number)
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
        # 弹出日期选择框
        def select_date():
            def on_date_select(event):
                """处理日期选择事件"""
                selected_date = self.cal.get_date()

                if self.start_date is None:
                    # 选择起始日期
                    self.start_date = selected_date
                    self.instruction_label.config(text="请点击选择结束日期")
                elif self.end_date is None:
                    # 选择结束日期
                    self.end_date = selected_date
                    update_label()
                    self.cal.master.destroy()  # 关闭日历框

            def update_label():
                # """更新主界面显示的日期范围"""
                # if self.start_date and self.end_date:
                #     self.label.config(text=f"起始日期: {self.start_date}, 结束日期: {self.end_date}")
                # else:
                #     self.label.config(text="未选择日期范围")
                # print(f"起始日期: {self.start_date}, 结束日期: {self.end_date}")
                pass
            self.date_select_top = tk.Toplevel(self.root)
            self.date_select_top.title("选择日期范围")
            self.start_date = None
            self.end_date = None
            # 获取当前日期
            now = datetime.datetime.now()
            # 创建日历控件
            self.cal = Calendar(self.date_select_top, selectmode="day", year=now.year, month=now.month, day=now.day)
            self.cal.pack(pady=10, padx=10)

            # 提示标签
            self.instruction_label = tk.Label(self.date_select_top, text="请点击选择起始日期", font=("Arial", 10))
            self.instruction_label.pack(pady=5)

            # 绑定日历点击事件
            self.cal.bind("<<CalendarSelected>>", on_date_select)
            # 阻塞主界面，直到日历框关闭
            self.root.wait_window(self.date_select_top)

        # 下拉框选中事件
        def on_select(event):
            # 取消全选状态，光标移到文本末尾
            self.combobox.selection_clear()
            # 聚焦到主窗口
            self.root.focus_force()
            # 获取选中的物品和下标
            item = event.widget.get()
            index = event.widget.current()
            print('选中物品下标:', index)
            # 获取选中物品的id
            self.selected_report_item = self.kucun[index]
            print('选中物品:', self.selected_report_item)
            # 更新treeview
            records = get_current_item_data(self.selected_report_item[1], self.selected_report_type)
            update_treeview(records)
            # 设置库存量
            self.top_frame_right_report_label.config(text=f"当前统计：{self.selected_report_item[2]}")

        
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
                elif period == "select":
                    if self.start_date is None or self.end_date is None:
                        print('未选择日期范围, 自动选择今日')
                        self.selected_report_type = 'today'
                        start = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
                        end = start + datetime.timedelta(days=1)
                    else:
                        # 将日期转为datetime
                        self.start_date = datetime.datetime.strptime(self.start_date, "%Y/%m/%d")
                        self.end_date = datetime.datetime.strptime(self.end_date, "%Y/%m/%d")
                        start = datetime.datetime(self.start_date.year, self.start_date.month, self.start_date.day, 0, 0, 0)
                        end = datetime.datetime(self.end_date.year, self.end_date.month, self.end_date.day, 0, 0, 0)
                        print('选择的日期范围:', start, end)
                else:
                    raise ValueError("时间段无效")
                
                # 设置时间标题
                # 设置标签文字
                self.top_time_label.config(text=f"当前时间范围：{start.strftime('%Y-%m-%d')} - {end.strftime('%Y-%m-%d')}")

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
            if type in ['today', 'week', 'month', 'select']:
                return filter_records(records, type)
            else:
                return records  # 全部返回
                
        # 获取起始日期的进货，销售统计
        def get_start_date_info(records):
            # 进货数量
            add_quantity = 0
            # 销售数量
            remove_quantity = 0
            # 售出金额
            sell_price = 0
            for record in records:
                if record[0] == 'add':
                    add_quantity += int(record[1])
                else:
                    remove_quantity += int(record[1])
                    sell_price += float(record[7])
            self.middle_frame_right_report_label.config(text=f"进货数量：{add_quantity}")
            self.bottom_frame_right_report_label.config(text=f"售出数量：{remove_quantity}")
            self.sell_price_frame_right_report.config(text=f"售出金额：{sell_price}")
            return add_quantity, remove_quantity

        # 更新treeview
        def update_treeview(records):
            # 获取起始日期的进货，销售统计
            get_start_date_info(records)
            # 清空treeview
            for item in self.tree_report.get_children():
                self.tree_report.delete(item)
            if not records:
                self.tree_report.insert('', 'end', values=('无数据', '无数据', '无数据', '无数据'))
                return
            # 插入数据
            for record in records:
                if record[0] == 'add' or record[0] == 'create':
                    set_type = '进货'
                else:
                    set_type = '销售'
                self.tree_report.insert('', 'end', values=(set_type, record[1], record[2], record[5].strftime("%Y-%m-%d %H:%M")))
        # 日期按钮事件
        def date_button_event(type):
            # 高亮按钮
            self.highlight_report_button(type)
            # 如果是自选，弹出日期选择框
            if type == 'select':
                
                select_date()
                

            # 更新选中type
            self.selected_report_type = type
            # 获取当前物品的记录
            records = get_current_item_data(self.selected_report_item[1], type)
            update_treeview(records)


        # tk.Label(self.main_frame, text="库存统计页面").pack()
        # 选中物品的id
        self.selected_report_item = None
        # 选中的type
        self.selected_report_type = 'today'
        # 添加库存统计的具体实现
        # 上下两个frame
        self.top_frame_report = tk.Frame(self.main_frame, height=40)
        self.top_frame_report.pack(fill=tk.X, expand=False)
        # # # 设置测试背景颜色
        # self.top_frame_report.config(bg='red')
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
        self.selected_report_item = self.kucun[0]
        print('当前选中物品:', self.selected_report_item)

        # 创建下拉框
        self.combobox = ttk.Combobox(self.top_frame_report, font=("Arial", 12, "bold"), textvariable=self.selected_item, width=15, state='readonly')
        self.combobox['values'] = item_names
        self.combobox.pack(side=tk.LEFT, padx=10)
        # 绑定选中事件
        self.combobox.bind("<<ComboboxSelected>>", on_select)

        # 添加三个按钮，今日，本周，本月   ###2025-1-28 在三个按钮前加入自选起始时间
        self.report_buttons['month'] = tk.Button(self.top_frame_report, text="本月", command=lambda: date_button_event('month'), font=("Arial", 12, "bold"),width=8, height=1)
        self.report_buttons['month'].pack(side=tk.RIGHT, padx=10)
        self.report_buttons['week'] = tk.Button(self.top_frame_report, text="本周", command=lambda: date_button_event('week'), font=("Arial", 12, "bold"),width=8, height=1)
        self.report_buttons['week'].pack(side=tk.RIGHT, padx=10)
        self.report_buttons['today'] = tk.Button(self.top_frame_report, text="今日", command=lambda: date_button_event('today'), font=("Arial", 12, "bold"),width=8, height=1)
        self.report_buttons['today'].pack(side=tk.RIGHT, padx=10)
        self.report_buttons['select'] = tk.Button(self.top_frame_report, text="自选", command=lambda: date_button_event('select'), font=("Arial", 12, "bold"),width=8, height=1)
        self.report_buttons['select'].pack(side=tk.RIGHT, padx=10)
        self.highlight_report_button('today')
        # 在上方添加frame
        self.top_frame_report_report = tk.Frame(self.bottom_frame_report, height=35)
        self.top_frame_report_report.pack(side=tk.TOP, fill=tk.X, expand=False)
        # # # 设置测试背景颜色
        # self.top_frame_report_report.config(bg='black')
        # 下侧frame加入左右两个frame
        self.left_frame_report = tk.Frame(self.bottom_frame_report, width=500)
        self.left_frame_report.pack(side=tk.LEFT, padx=(20,0), fill=tk.Y)
        # # # 设置测试背景颜色
        # self.left_frame_report.config(bg='yellow')
        self.right_frame_report = tk.Frame(self.bottom_frame_report)
        self.right_frame_report.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        # # # 设置测试背景颜色
        # self.right_frame_report.config(bg='green')

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

        # 右侧frame加入三个frame，分别是库存统计，进货统计，销售统计，售出金额
        self.top_frame_right_report = tk.Frame(self.right_frame_report, height=100)
        self.top_frame_right_report.pack(side=tk.TOP, fill=tk.X, expand=1)
        
        self.middle_frame_right_report = tk.Frame(self.right_frame_report, height=100)
        self.middle_frame_right_report.pack(side=tk.TOP, fill=tk.X, expand=1)

        self.bottom_frame_right_report = tk.Frame(self.right_frame_report, height=100)
        self.bottom_frame_right_report.pack(side=tk.TOP, fill=tk.X, expand=1)

        self.sell_price_frame_right_report = tk.Frame(self.right_frame_report, height=100)
        self.sell_price_frame_right_report.pack(side=tk.TOP, fill=tk.X, expand=1)

        # 添加三个标签按钮
        self.top_frame_right_report_label = tk.Label(self.top_frame_right_report, text=f"当前库存: {self.selected_report_item[3]}", font=("Arial", 12, "bold"))
        self.top_frame_right_report_label.pack(side=tk.LEFT, padx=20)
        self.middle_frame_right_report_label = tk.Label(self.middle_frame_right_report, text="进货: ", font=("Arial", 12, "bold"))
        self.middle_frame_right_report_label.pack(side=tk.LEFT, padx=20)
        self.bottom_frame_right_report_label = tk.Label(self.bottom_frame_right_report, text="售出: ", font=("Arial", 12, "bold"))
        self.bottom_frame_right_report_label.pack(side=tk.LEFT, padx=20)
        # 售出金额
        self.sell_price_frame_right_report = tk.Label(self.sell_price_frame_right_report, text="售出金额: ", font=("Arial", 12, "bold"))
        self.sell_price_frame_right_report.pack(side=tk.LEFT, padx=20)


        # 默认为第一个物品的当天数据
        # 获取当天的库存数据
        current_item_data = get_current_item_data(self.selected_report_item[1], 'today')
        print('当前物品当天数据:', current_item_data)
        # 更新treeview
        update_treeview(current_item_data)


    
    # 创建事件日志页面
    def create_event_log(self):
        # 日志页面鼠标双击事件
        def on_click_double_event(event):
            # 获取鼠标指针所在行的ID
            row_id = self.tree_event.identify_row(event.y)
            # 获取行数据
            log_data = self.tree_event.item(row_id, "values")
            log_data = self.event_log[self.tree_event.index(row_id)]

            # 可能选中的是空白处
            if not log_data:
                print('双击选中空白处')
                return
            
            # 弹出新窗口，显示详细信息
            self.dialog_log = tk.Toplevel(self.root)
            self.dialog_log.title("物品详细信息")
            self.dialog_log.geometry("300x150")
            # 不可改变大小
            self.dialog_log.resizable(False, False)
            # 禁止操作主界面
            self.root.attributes("-disabled", True)
            # 在屏幕中央显示
            x = (self.screen_width - 300) // 2
            y = (self.screen_height - 150) // 2
            self.dialog_log.geometry(f"300x150+{x}+{y}")
            # 设置关闭事件
            self.dialog_log.protocol("WM_DELETE_WINDOW", on_closing_dialog_log)
            # 聚焦到弹窗
            self.dialog_log.focus_force()
            # 操作内容
            tk.Label(self.dialog_log, text="操作内容:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
            text_log = tk.Text(self.dialog_log, width=27, height=9)
            text_log.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
            # 添加滑轮
            # scrollbar_log = tk.Scrollbar(self.dialog_log)
            # scrollbar_log.grid(row=0, column=2, sticky='ns')
            # scrollbar_log.config(command=text_log.yview)
            # text_log.config(yscrollcommand=scrollbar_log.set)
            text_log.insert('end', log_data[3])
            text_log.config(state='disabled')
        
        # 关闭弹窗
        def on_closing_dialog_log():
            print("关闭弹窗")
            self.root.attributes("-disabled", False)
            # 聚焦到主窗口
            self.root.focus_force()
            self.dialog_log.destroy()



        # 添加treeview和滑轮
        self.canvas_event = tk.Canvas(self.main_frame)
        # 事件描述|@| 操作员工id|@| 操作员工|@| 操作内容内容|@| 操作时间
        columns = {"":60 ,"事件描述":150, "操作员工id":100, "操作员工":100, "操作内容":200, "操作时间":170}
        self.tree_event = ttk.Treeview(self.canvas_event, columns=list(columns), show='headings')
        self.scrollbar_event = tk.Scrollbar(self.main_frame, orient='vertical')
        for text, width in columns.items():
            self.tree_event.heading(text, text=text, anchor='center')
            self.tree_event.column(text, anchor='center', width=width, stretch=True)
        self.tree_event.pack(fill=tk.BOTH, expand=True)
        self.canvas_event.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar_event.pack(side=tk.RIGHT, fill='y')
        self.scrollbar_event.configure(command=self.tree_event.yview)
        self.tree_event.configure(yscrollcommand=self.scrollbar_event.set)
        # 获取事件日志数据
        self.event_log = get_event_log()
        # 倒转列表
        self.event_log.reverse()
        # 插入数据
        for index, record in enumerate(self.event_log, start=1):
            try:
                time = datetime.datetime.strptime(record[4], "%Y-%m-%d %H:%M:%S.%f")  # 转为datetime
            except:
                time = datetime.datetime.strptime(record[4], "%Y-%m-%d %H:%M:%S")  # 转为datetime
            self.tree_event.insert('', 'end', values=(index, record[0], record[1], record[2], record[3][:14]+'...', time.strftime("%Y-%m-%d %H:%M")))
        # 绑定双击事件
        self.tree_event.bind('<Double-1>', on_click_double_event)

        

    
    # 添加物品事件
    def add_item_event(self):
        # 双击事件

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
        self.dialog_add_item_category.geometry(f"420x280+{x}+{y}")
        # 物品名称
        tk.Label(self.dialog_add_item_category, text="物品名称:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        item_name = tk.Entry(self.dialog_add_item_category)
        item_name.grid(row=0, column=1, padx=(10,160), pady=5, sticky="ew")
        item_name.config(width=10)
        # 价格
        tk.Label(self.dialog_add_item_category, text="价格:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        item_price = tk.Entry(self.dialog_add_item_category)
        item_price.grid(row=1, column=1, padx=(10,160), pady=5, sticky="ew")
        item_price.config(width=10)
        # 数量
        tk.Label(self.dialog_add_item_category, text="数量:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        item_quantity = tk.Entry(self.dialog_add_item_category)
        item_quantity.grid(row=2, column=1, padx=(10,160), pady=5, sticky="ew")
        item_quantity.config(width=10)
        # 第三行添加备注
        tk.Label(self.dialog_add_item_category, text="备注：").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        # 添加备注框
        comment_quantity = tk.Text(self.dialog_add_item_category, width=27, height=8)
        comment_quantity.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # 添加按钮
        tk.Button(self.dialog_add_item_category, text="添加", height=2, width=5, command=lambda: self.category_add_commit_item_event(item_name.get(), item_price.get(), item_quantity.get(), comment_quantity.get("1.0", "end-1c"))).grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")


    # 提交添加物品事件
    def category_add_commit_item_event(self, item_name, item_price, item_quantity, comment_text): 
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
        # 4、验证price是否为数字
        if not is_price(item_price) :
            return
        # 验证操作人员，验证通过才能进行操作
        verify_result = verify_user_ui(self.dialog_add_item_category)
        if not verify_result:
            return
        # 生成唯一ID
        id = generate_id('item')
        print('添加物品:', item_name, id, item_price, item_quantity, comment_text)
        # 生成 
        # 去掉备注中的换行符
        comment_text = comment_text.replace('\n', '  ')
        # 备份文件
        write_with_backup(kucun_path)
        write_with_backup(modify_inventory_log_path)
        write_with_backup(event_log_path)
        write_with_backup(f'{items_folder_path}{id}.txt')
        # 写入库存文件
        with open(kucun_path, 'a', encoding='utf-8') as file:
            file.write(f"{item_name}|@|{id}|@|{item_price }|@|{item_quantity}|@|{comment_text}\n")
        # 写入库存修改日志
        with open(modify_inventory_log_path, 'a', encoding='utf-8') as file:
            file.write(f'{item_name}|@| add|@| {item_quantity}|@| {item_quantity}|@| {verify_result[1]}|@| {verify_result[0]}|@| {datetime.datetime.now()}\n')
        # 写入事件日志
        with open(event_log_path, 'a', encoding='utf-8') as file:
            file.write(f'添加新物品|@| {verify_result[0]}|@| {verify_result[1]}|@| 货物: {item_name}, 价格: {item_price}, 数量: {item_quantity}, 备注: {comment_text}|@| {datetime.datetime.now()}\n')
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
        item_name, item_id, item_price, item_quantity, item_comment = self.kucun[self.selected_item_index]
        print('要删除的物品信息:', item_name, item_id, item_price, item_quantity, item_comment)

        # 读取库存文件
        self.kucun = load_kucun()
        # 删除物品
        self.kucun.pop(self.selected_item_index)
        # 备份文件
        write_with_backup(kucun_path)
        write_with_backup(modify_inventory_log_path)
        write_with_backup(event_log_path)
        # 写入文件
        with open(kucun_path, 'w', encoding='utf-8') as file:
            file.write("name|@| id|@| price|@| num|@| command\n")
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
            file.write(f'删除物品|@| {verify_result[0]}|@| {verify_result[1]}|@| 货物: {item_name}, 数量: {item_quantity}, 备注: {item_comment}|@| {datetime.datetime.now()}\n')
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
        def category_modify_commit_item_event(self, item_name_entry, item_price_entry, comment_text): 
            # 原来物品信息
            item_name, item_id, item_price, item_quantity, item_comment = self.kucun[self.selected_item_index]
            print('修改后物品:', item_name_entry, item_id, item_price, item_quantity, comment_text)
            if not is_price(item_price_entry):
                return

            # 修改物品信息
            self.kucun[self.selected_item_index] = [item_name_entry, item_id, item_price_entry, item_quantity, comment_text]

            # 备份文件
            write_with_backup(kucun_path)
            write_with_backup(event_log_path)
            # 写入库存文件
            with open(kucun_path, 'w', encoding='utf-8') as file:
                file.write("name|@| id|@| price|@| num|@| command\n")
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
                # 判断价格是否改变
                if item_price != item_price_entry:
                    file.write(f'修改物品信息|@| {verify_result[0]}|@| {verify_result[1]}|@| 货物: {item_name}, 价格: {item_price}, 备注: {item_comment}；修改为--->：货物：{item_name_entry}，价格：{item_price_entry}，备注：{comment_text}|@| {datetime.datetime.now()}\n')
                else:
                    file.write(f'修改物品信息|@| {verify_result[0]}|@| {verify_result[1]}|@| 货物: {item_name}, 备注: {item_comment}；修改为--->： 货物：{item_name_entry}，备注：{comment_text}|@| {datetime.datetime.now()}\n')
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
        item_name, item_id, item_prece, item_quantity, item_comment = self.kucun[self.selected_item_index]
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
        tk.Label(self.dialog_modify_item_category, text="物品名称:").grid(row=0, column=0, padx=6, pady=5, sticky="w")
        item_name_entry = tk.Entry(self.dialog_modify_item_category)
        item_name_entry.grid(row=0, column=1, padx=(10,280), pady=5, sticky="ew")
        item_name_entry.config(width=10)
        item_name_entry.insert(0, item_name)

        # 价格
        tk.Label(self.dialog_modify_item_category, text="价格:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        item_price_entry = tk.Entry(self.dialog_modify_item_category)
        item_price_entry.grid(row=1, column=1, padx=(10,280), pady=5, sticky="ew")
        item_price_entry.config(width=10)
        item_price_entry.insert(0, item_prece)

        # 第二行添加备注
        tk.Label(self.dialog_modify_item_category, text="备注：").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        # 添加备注框
        comment_quantity = tk.Text(self.dialog_modify_item_category, width=27, height=8)
        comment_quantity.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        # 添加默认值
        comment_quantity.insert(tk.END, item_comment)

        # 第三行加入空白标签
        tk.Label(self.dialog_modify_item_category, text="").grid(row=3, column=0, columnspan=2)

        # 添加按钮
        tk.Button(self.dialog_modify_item_category, text="修改", height=2, width=5, command=lambda: category_modify_commit_item_event(self, item_name_entry.get(), item_price_entry.get(), comment_quantity.get("1.0", "end-1c"))).grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    
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