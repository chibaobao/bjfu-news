from whoosh.index import create_in,open_dir
from whoosh import fields
from whoosh.fields import TEXT,ID
from jieba.analyse import ChineseAnalyzer
from whoosh import index
from whoosh.qparser import QueryParser

class MyWhoosh:
    index_name = ""
    def __init__(self,path,index_name):
        self.index_name = index_name
        analyzer = ChineseAnalyzer()  # 导入中文分词工具
        schema = fields.Schema(title=TEXT(stored=True), path=ID(stored=True),
                               content=TEXT(stored=True, analyzer=analyzer))
        try:
            self.ix = index.open_dir(path, index_name)
            print("use old index")
        except:
            self.ix = create_in(path, schema=schema, indexname= index_name)  # path 为索引创建的地址，indexname为索引名称
            print("creat net index")

    def insert( self, path, title, content):
        writer = self.ix.writer()
        writer.delete_by_term("path", path) # 为了保证唯一性，先尝试将就path数据删除
        writer.add_document(title = title, path= path, content = content)  # 此处为添加的内容
        writer.commit()

    def find(self,text):
        searcher = self.ix.searcher()
        ret_list = []
        parser = QueryParser("content", schema=self.ix.schema)
        try:
            word = parser.parse(text)
        except:
            word = None
        if word is not None:
            hits = searcher.search(word)
            for hit in hits:
                ret_list.append(dict(hit))
        return ret_list
    def delete_by_path(self,path):
        writer = self.ix.writer()
        writer.delete_by_term("path", path)
        writer.commit()

if __name__ == "__main__":
    wh = MyWhoosh("../indexPath",'myindex')
    wh.delete_by_path("/a/b/cd")
    wh.insert("id1","title1","我爱中国")
    print(wh.find("中国"))