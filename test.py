import tkinter as tk

# 创建主窗口
root = tk.Tk()
root.title("主窗口")
root.geometry("300x200")

# 创建一个窗口前置功能
def create_front_window():
    top = tk.Toplevel(root)
    top.title("前置窗口")
    top.geometry("200x100")
    # 确保仅在主窗口前置
    top.transient(root)
    top.focus_force()

# 添加按钮触发窗口前置
btn = tk.Button(root, text="弹出前置窗口", command=create_front_window)
btn.pack(pady=50)

root.mainloop()
