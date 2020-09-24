import jieba

f0 = open('fields.txt', 'r', encoding='utf-8', newline='')
list_fields = []
for line in f0.readlines():
    list_fields.append(line.split())
fields = dict(list_fields)

f1 = open('stopwords.txt', 'r', encoding='utf-8', newline='')
stopwords = []
for line in f1.readlines():
    stopwords.append(line.strip('\r\n'))

jieba.load_userdict("userdict.txt")

title = "小白课堂 | 区块链里的智能合约VS传统合约"

result = jieba.lcut(title, HMM=False)
print('分割形式', result)

write_dict = {}
stop_dict = {}
for word in result:
    if word in stopwords:
        print("DON'T WRITE")
        stop_dict[title] = word
        break
    elif word in fields.keys():
        write_dict[title] = fields[word]
        break
if not stop_dict and not write_dict:
    write_dict[title] = '待定'

print('行业类型分类', write_dict)

sen = '区块链<\em>部门例会'
print(sen.replace('<\em>', ''))
