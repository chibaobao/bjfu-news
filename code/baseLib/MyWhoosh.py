# -*- coding: utf-8 -*-
from whoosh.index import create_in,open_dir
from whoosh import fields
from whoosh.fields import TEXT,ID
from jieba.analyse import ChineseAnalyzer
from whoosh import index
from whoosh.qparser import QueryParser

class MyWhoosh:
    '''
    对whoosh的简单封装，提供增删查3种方法
    '''
    index_name = ""
    def __init__(self,path,index_name):
        '''
        创建一个MyWhoosh索引类，如果指定路径下的索引存在则直接打开，若不存在就创建新的
        :param path: 索引类要存放的文件夹路径
        :param index_name: 索引名称（一个文件夹下可以存放多个索引）
        '''
        self.index_name = index_name
        analyzer = ChineseAnalyzer()  # 导入中文分词工具
        schema = fields.Schema(title=TEXT(stored=True), path=ID(stored=True),
                               content=TEXT(stored=True, analyzer=analyzer))
        try:
            self.ix = index.open_dir(path, index_name)
            print("索引文件已经存在，use old index")
        except:
            self.ix = create_in(path, schema=schema, indexname= index_name)  # path 为索引创建的地址，indexname为索引名称
            print("没有检测到旧索引文件，creat net index")

    def insert( self, path, title, content):
        '''
        添加一条索引，一个索引由三部分勾选（文章id, 文章标题, 文章内容）
        这里的插入会保证path的唯一性，也就是如果该path已经存在，就会覆盖原理path的信息
        :param path: 注意这里的path不是一定是路径，path是一个id,因为文章的路径都是唯一的，所以一般path是文章的路径
        :param title: 文章的标题
        :param content: 文章的内容
        :return:
        '''
        writer = self.ix.writer()
        writer.delete_by_term("path", path) # 为了保证唯一性，先尝试将就path数据删除
        writer.add_document(title = title, path= path, content = content)  # 此处为添加的内容
        writer.commit()

    def find(self,text):
        '''
        通过关键字查找一篇文章
        :param text: 关键字
        :return: 返回一个dict，包括path, title, content
        '''
        searcher = self.ix.searcher()
        ret_list = []
        parser = QueryParser("content", schema=self.ix.schema)
        try:
            word = parser.parse(text)
        except:
            word = None
        if word is not None:
            hits = searcher.search(word,limit = None)
            for hit in hits:
                ret_list.append(dict(hit))
        return ret_list
    def delete_by_path(self,path):
        '''
        通过文章的path(id)删除一条数据
        :param path: 文章的path（id）
        :return:
        '''
        writer = self.ix.writer()
        writer.delete_by_term("path", path)
        writer.commit()

if __name__ == "__main__":
    wh = MyWhoosh("../indexPath",'myindex')
    wh.delete_by_path("/a/b/cd")
    wh.insert("id1","title1","我爱中国")
    print(wh.find("中国"))