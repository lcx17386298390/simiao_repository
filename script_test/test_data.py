import tkinter as tk
from tkcalendar import Calendar

class DateRangePicker:
    def __init__(self, root):
        self.root = root
        self.root.title("日期范围选择器")

        # 起始日期和结束日期
        self.start_date = None
        self.end_date = None

        # 创建按钮，点击后弹出日历框
        self.pick_button = tk.Button(root, text="选择日期范围", command=self.open_calendar)
        self.pick_button.pack(pady=20)

        # 显示选择的日期范围
        self.label = tk.Label(root, text="未选择日期范围", font=("Arial", 12))
        self.label.pack(pady=10)

    def open_calendar(self):
        """打开日历框"""
        top = tk.Toplevel(self.root)
        top.title("选择日期范围")

        # 创建日历控件
        self.cal = Calendar(top, selectmode="day", year=2024, month=1, day=1)
        self.cal.pack(pady=10, padx=10)

        # 提示标签
        self.instruction_label = tk.Label(top, text="请点击选择起始日期", font=("Arial", 10))
        self.instruction_label.pack(pady=5)

        # 绑定日历点击事件
        self.cal.bind("<<CalendarSelected>>", self.on_date_select)

    def on_date_select(self, event):
        """处理日期选择事件"""
        selected_date = self.cal.get_date()

        if self.start_date is None:
            # 选择起始日期
            self.start_date = selected_date
            self.instruction_label.config(text="请点击选择结束日期")
        elif self.end_date is None:
            # 选择结束日期
            self.end_date = selected_date
            self.update_label()
            self.cal.master.destroy()  # 关闭日历框

    def update_label(self):
        """更新主界面显示的日期范围"""
        if self.start_date and self.end_date:
            self.label.config(text=f"起始日期: {self.start_date}, 结束日期: {self.end_date}")
        else:
            self.label.config(text="未选择日期范围")

# 创建主窗口
root = tk.Tk()
app = DateRangePicker(root)
root.mainloop()