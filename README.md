# simiao_repository
简易仓库统计软件

# 2024-12-20
突然想到一件事，不做数据库，使用txt存储的话还是应该每个物品创建一个单独的记录表，因为涉及到修改名称等，要修改库存文件，读取后筛选耗时。
# 2024-12-20
回应上方疑问，仔细考虑后，该名称不涉及到大范围修改，因为ID是唯一的，只需要修改库存表的名称，可以获取到ID；但是涉及到修改记录可能会太多，后续加载慢，应该单独写

打包命令pyinstaller --onefile --windowed --icon=files/icon.ico main_ui.py