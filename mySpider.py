import requests
import re
import csv
import jieba

# 获取想要搜索的关键词
word = input("请输入想要搜索的关键词： ")

# 创建csv
f = open('results.csv', 'w', encoding='utf-8', newline='')
csv_writer = csv.writer(f)
csv_writer.writerow(["日期", "标题", "涉及方", "涉及方类型", "细分行业", "行业类型", "链接"])

jieba.load_userdict("userdict.txt")

# 空列表用于存储所有写入的消息，去重时用
all_msgs = []


# 对行业类型进行分类
def classify_field(title):
    f0 = open('fields.txt', 'r', encoding='utf-8', newline='')
    list_fields = []
    for line in f0.readlines():
        list_fields.append(line.split())
    fields = dict(list_fields)

    f1 = open('stopwords.txt', 'r', encoding='utf-8', newline='')
    stopwords = []
    for line in f1.readlines():
        stopwords.append(line.strip('\r\n'))

    result = jieba.lcut(title, cut_all=False, HMM=False)

    write_dict = {}
    stop_dict = {}
    for word in result:
        if word in stopwords:
            stop_dict[title] = 'STOP WRITE'
        if word in fields.keys():
            write_dict[title] = [word, fields[word]]
            break

    if stop_dict:
        write_dict[title] = None
    if not stop_dict and not write_dict:
        write_dict[title] = [result[0], '待定']

    return write_dict[title]


# 对涉及方进行分类
def classify_party(title, link, date):
    if classify_field(title) is not None:

        field = classify_field(title)[0]
        field_type = classify_field(title)[1]

        f1 = open('areas.txt', 'r', encoding='utf-8', newline='')
        f1.readline()
        areas = []
        for line in f1:
            areas.append(line.strip('\r\n'))

        f2 = open('parties.txt', 'r', encoding='utf-8', newline='')
        list_parties = []
        for line in f2.readlines():
            list_parties.append(line.split())
        parties = dict(list_parties)

        result = jieba.lcut(title, cut_all=False, HMM=False)

        write_msg = []
        for word in result:
            if word in parties.keys():
                msg = [date, title, word, parties[word], field, field_type, link]
                # 去重
                if msg not in all_msgs:
                    csv_writer.writerow(msg)
                    write_msg.append(msg)
                    all_msgs.append(msg)
                break
            elif word in areas:
                msg = [date, title, word, '地区', field, field_type, link]
                if msg not in all_msgs:
                    csv_writer.writerow(msg)
                    write_msg.append(msg)
                    all_msgs.append(msg)
                break

        if not write_msg:
            msg = [date, title, result[0], '其他', field, field_type, link]
            if msg not in all_msgs:
                csv_writer.writerow(msg)
                write_msg.append(msg)
                all_msgs.append(msg)


# 爬取网页
def baidu(page):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/69.0.3497.100 Safari/537.36'}
    num = (page - 1) * 10
    url = 'https://www.baidu.com/s?tn=news&rtt=4&bsst=1&cl=2&wd=' + word + '&pn=' + str(num) + '.html'
    res = requests.get(url, headers=headers).text

    p_href = '<h3 class="news-title_1YtI1">.*?<a href="(.*?)"'
    p_title = '<h3 class="news-title_1YtI1">.*?>(.*?)<!--/s-text-->'
    p_source = '<span class="c-color-gray c-font-normal c-gap-right">(.*?)</span>'
    p_date = '<span class="c-color-gray2 c-font-normal">(.*?)</span>'

    href = re.findall(p_href, res, re.S)
    title = re.findall(p_title, res, re.S)
    source = re.findall(p_source, res, re.S)
    date = re.findall(p_date, res, re.S)

    for i in range(len(title)):
        title[i] = title[i].strip()
        title[i] = title[i].replace('<em>', '')
        title[i] = title[i].replace('</em>', '')
        title[i] = title[i].replace('<!--s-text-->', '')

        source[i] = source[i].strip()
        date[i] = date[i].strip()
        msg_title = title[i]
        msg_link = href[i]
        print(str(i + 1) + '.' + msg_title + '(' + date[i] + '-' + source[i] + ')')
        print(msg_link)

        classify_party(msg_title, msg_link, date[i])


# 一般当天新闻10页左右即可爬完，可根据需求增加页数
for i in range(10):
    baidu(i + 1)
    print('第' + str(i + 1) + '页爬取成功')
