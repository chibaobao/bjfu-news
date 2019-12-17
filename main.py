from code.BjfuHtml import GetBjfuHtmls
from code.baseLib.MyWhoosh import MyWhoosh
import pymongo
from flask import Flask
from flask import  request as Frequest
import json
import os


def mkdir(path):
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        return True
    else:
        return False


mkdir("indexPath")
wh = MyWhoosh("./indexPath",'myindex')
server = Flask(__name__,static_url_path='')

def main():
    #数据库
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["mydatabase"]
    mycol = mydb["html"]
    result = mycol.delete_many({}) # 清空数据库，重新开始爬取数据
    #爬虫
    start_url = "http://news.bjfu.edu.cn"
    bjfu = GetBjfuHtmls(start_url)
    bjfu.start(mycol)
    #搜索引擎
    # wh = MyWhoosh("./indexPath",'myindex')
    for x in mycol.find({}, {"_id": 1, "title": 1, "text": 1}):
        wh.insert(x["_id"],x["title"],x["text"])
    #查询
    print("测试，查找使命：",wh.find("使命"))

@server.route('/')
def home():
    return server.send_static_file('./index.html')#index.html在static文件夹下

@server.route('/searchMedicine',methods=['get','post'])
def searchMedicine():
    context = Frequest.values.get('name')
    result = wh.find(context)
    return json.dumps(result, ensure_ascii=False)

if __name__ == "__main__":
    # url3 = "http://news.bjfu.edu.cn"
    # bjfu = GetBjfuHtmls(url3)
    # bjfu.start()
    main()
    server.run(port=5000, host='0.0.0.0')