import tkinter as tk

root = tk.Tk()
root.geometry("600x300")

left_frame = tk.Frame(root, bg="red", width=100, height=300)
left_frame.pack(side="left", padx=(20, 0), fill="y")

right_frame = tk.Frame(root, bg="blue", width=100, height=300)
right_frame.pack(side="right", padx=(0, 20), fill="y")

root.mainloop()

# import tkinter as tk

# root = tk.Tk()
# root.geometry("600x300")

# left_frame = tk.Frame(root, bg="red", width=100, height=300)
# left_frame.grid(row=0, column=0, sticky="w")

# right_frame = tk.Frame(root, bg="blue", width=100, height=300)
# right_frame.grid(row=0, column=1, sticky="e")

# root.columnconfigure(0, weight=1)
# root.columnconfigure(1, weight=1)

# root.mainloop()
