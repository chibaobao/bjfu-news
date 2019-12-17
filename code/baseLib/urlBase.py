from urllib import request
import chardet
from bs4 import    BeautifulSoup
from urllib.parse import urlparse
import re
import requests
from urllib.parse import urljoin

class URLList:
    '''
    URLList是一个简单的url容器，当url数据量变多时要重新实现URLlist
    提供增删查三种方法
    '''
    def __init__(self):
        self.__urlList = []
    def insert(self,url):
        if url in self.__urlList:
            return False
        else:
            self.__urlList.append(url)
            return True
    def is_have(self,url):
        if url in self.__urlList:
            return True
        else:
            return False
    def get_url(self):
        ret = self.__urlList[-1]
        del self.__urlList[-1]
        return ret

    def __len__(self):
        return len(self.__urlList)


class Scheduler:
    '''
    一个简单的调度器，容器采用的URLList
    只提供两个方法：insert和get，使用者无需关心是否回插入重复的url，也就是说调度器自动避免访问重复的页面
    同时可以用len方法查看调度器中还有多少url要访问
    原理：同时有两个容器一个保存要访问的url一个保存历史url,url被get之后会自动从要访问的url容器放入历史容器中
    '''
    __new_url = URLList() #用来存储将要访问的url
    __history_url = URLList() #用来存储未访问的url
    def insert(self,url):
        '''
        插入一个url，若url曾经被插入过，则不会再被插入
        :param url: 要插入的url
        :return: 无
        '''
        if self.__history_url.is_have(url) != True and self.__new_url.is_have(url) != True:#在历史记录里有
            self.__new_url.insert(url)
        return
    def get(self):
        '''
        获取一个url
        :return:返回一个url
        '''
        if len(self.__new_url) > 0:
            ret = self.__new_url.get_url()
            self.__history_url.insert(ret)
            return ret
        else:
            return None

    def __len__(self):
        return len(self.__new_url)

class HtmlPage:
    '''
    HtmlPage:页面分析类，用来对一个页面进行分析
    使用方式：
    1.用一个url初试化
    2.调用request进行请求
    3.  get_html获取整个html（shtring类型）
        get_all_url获取页面中的全部url
        利用self.soup（BeautifulSoup(self.html_text, 'lxml') 的返回）对页面进行分析
    '''
    decode = None
    html_text = ""
    headers_dict = {}
    url_str = "" #整个url
    url_scheme = "" #eg:https or http
    url_netloc = "" #域名部分 eg:blog.csdn.net
    url_path = ""
    def __init__(self,url_str,headers_dict = None):
        self.url_str = url_str
        if headers_dict == None:
            self.headers_dict["ser-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
        else:
            self.headers_dict = headers_dict
        res = urlparse(url_str)
        self.url_scheme = res.scheme #http or https
        self.url_netloc = res.netloc
        path_list = res.path.split("/")
        if len(path_list) > 0:
            path_list.pop(0)
        if len(path_list) > 0:
            path_list.pop(-1)
        for path_i in path_list:
            self.url_path = self.url_path + "/" + path_i
    def request(self):
        '''
        进行页面请求
        :return:
        '''
        req_html = request.Request(self.url_str)
        for key,value in self.headers_dict.items():
            req_html.add_header(key,value)
        # req_html.add_header('Accept-Encoding', 'gzip, deflate')
        req_html_ret = request.urlopen(req_html).read()
        character_encoding = chardet.detect(req_html_ret)["encoding"]
        if character_encoding is None:
            self.html_text = req_html_ret.decode("utf-8",errors = 'ignore')
        else:
            self.html_text = req_html_ret.decode(character_encoding,errors = 'ignore')
        self.soup = BeautifulSoup(self.html_text, 'lxml')

    def get_html(self):
        '''
        获取整个html页面
        :return: 返回一个string格式的html页面
        '''
        return self.html_text


    def get_all_url(self):
        '''
        返回该页面的url
        :return: 两个list，第一list是该域名下的url，第二个list是其他域名下的url
        '''
        url_list = []
        other_url_list = []
        links = self.soup.find_all('a') #article
        for link in links:
            url = link.get('href')
            if url is not None and url != "": #url非空
                res = urlparse(url)
                if(res.scheme == "http" or res.scheme == "https" or res.scheme == ""): #首先是一个合法网址（而不是邮箱地址之类的）
                    if res.netloc == self.url_netloc or res.netloc == "": # 本域名下的信息
                        url_list.append(urljoin(self.url_str, url))
                    else:
                        other_url_list.append(url)
        return  url_list,other_url_list


