raw = open('sample.txt','rb').read()
print('raw repr', raw)
print('utf8 ignore:', raw.decode('utf-8', errors='ignore'))
print('utf16:', raw.decode('utf-16', errors='ignore'))
