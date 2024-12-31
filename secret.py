import os
# def xor_encrypt_decrypt_line(line, key):
#     return ''.join(chr(ord(char) ^ ord(key[i % len(key)])) for i, char in enumerate(line))

import base64

def xor_encrypt_decrypt_line(line, key):
    # 使用 XOR 对每个字符进行加密/解密
    encrypted_chars = [chr(ord(char) ^ ord(key[i % len(key)])) for i, char in enumerate(line)]
    
    # 将加密后的字符列表合并成一个字符串
    encrypted_line = ''.join(encrypted_chars)
    
    # 对加密后的字符串进行 Base64 编码，保证输出的字符都可以打印
    encoded_line = base64.b64encode(encrypted_line.encode('utf-8')).decode('utf-8')
    
    return encoded_line

# 解密时先进行 Base64 解码，然后再 XOR 操作
def xor_decrypt_line(encrypted_line, key):
    # 对 Base64 编码的数据进行解码
    decoded_line = base64.b64decode(encrypted_line.encode('utf-8')).decode('utf-8')
    
    # 使用 XOR 进行解密
    decrypted_chars = [chr(ord(char) ^ ord(key[i % len(key)])) for i, char in enumerate(decoded_line)]
    
    # 将解密后的字符列表合并成一个字符串
    decrypted_line = ''.join(decrypted_chars)
    
    return decrypted_line

key = "secret_key"  # 密钥
users_path = 'files/users.txt'  # 用户信息文件路径
users = {}
if os.path.exists(f'{users_path}'):
    with open(f'{users_path}', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines[1:]:
            id, job_number, name, password = line.strip().split('|@| ')
            password = xor_encrypt_decrypt_line(password, key)
            users[job_number] = {'id': id, 'name': name, 'password': password}
print(users)

# 写入员工文件
with open(users_path, 'w', encoding='utf-8') as file:
    # 写入表头
    file.write("id|@| job_number|@| name|@| password\n")
    # 重新写入员工文件
    for job_number, values in users.items():
        file.write(f"{values['id']}|@| {job_number}|@| {values['name']}|@| {values['password']}\n")

# # 加密或解密
# processed_lines = [xor_encrypt_decrypt_line(line.strip(), key) for line in lines[1:]]

# # 保存或继续处理
# with open("output.txt", "w", encoding="utf-8") as f:
#     f.writelines(line + '\n' for line in processed_lines)