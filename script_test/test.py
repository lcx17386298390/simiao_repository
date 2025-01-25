import random

# 读取文件内容
with open('D:\MyCodes\simiao_repertory\script_test\kucun.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 处理每一行
new_lines = []
for line in lines:
    parts = line.strip().split('|@|')
    if len(parts) == 4:
        # 生成一个随机价格（假设价格范围在1到100之间）
        price = str(random.randint(1, 100))
        # 在id后面插入随机价格
        parts.insert(2, price)
        new_line = '|@|'.join(parts)
        new_lines.append(new_line)

# 将处理后的内容写回文件
with open('your_file_modified.txt', 'w', encoding='utf-8') as file:
    for line in new_lines:
        file.write(line + '\n')

print("处理完成，结果已写入your_file_modified.txt")