import tkinter as tk
from tkinter import ttk

# 创建主窗口
root = tk.Tk()
root.title("Treeview 示例")

# 创建 Treeview 小部件
treeview = ttk.Treeview(root, columns=("col1", "col2", "col3"))

# 配置列
# treeview.heading("#0", text="ID")  # 第一列标题
treeview.heading("col1", text="姓名")
treeview.heading("col2", text="工号")
treeview.heading("col3", text="密码")

# 隐藏第一列
treeview.column("#0", width=0, stretch=tk.NO)  # 设置第一列宽度为0，且不允许拉伸

# 插入数据，第一列通过 text 属性插入值，但该列会被隐藏
treeview.insert("", "end", text="root_001", values=("张三", "001", "password123"))
treeview.insert("", "end", text="root_002", values=("李四", "002", "12345678"))
treeview.insert("", "end", text="root_003", values=("王五", "003", "abc123"))

# 单击事件处理函数
def on_item_click(event):
    # 获取选中项
    selected_item = treeview.selection()
    if selected_item:
        # 获取选中项的文本，即隐藏列的值
        item_text = treeview.item(selected_item[0], "text")
        print(f"选中行的隐藏列值: {item_text}")
        # 获取选中项的值
        item_values = treeview.item(selected_item[0], "values")
        print(f"选中行的值: {item_values}")

# 绑定单击事件
treeview.bind("<ButtonRelease-1>", on_item_click)

# 显示 Treeview
treeview.pack(fill=tk.BOTH, expand=True)

# 启动 GUI
root.mainloop()
