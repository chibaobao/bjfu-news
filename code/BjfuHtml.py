from code.baseLib.urlBase import Scheduler,HtmlPage
from bs4 import    BeautifulSoup
from urllib.parse import urlparse
import requests
import re
import time


class GetBjfuHtmls:
    '''
    针对绿色新闻网的爬虫，用一个起始url进行初试化
    调用start启动爬虫
    主要包括一个 Scheduler（调度器）：把将要访问的url nset到调度器，然后每次要访问页面时从调度器get一个url
    若要实现爬取其他网站可以重新实现start方法
    '''''
    decode = None
    url_scheme = ""  # eg:https or http
    url_netloc = ""  # 域名部分 eg:blog.csdn.net
    scheduler = Scheduler()

    def __init__(self, start_url):
        #爬虫部分
        res = urlparse(start_url)
        self.url_scheme = res.scheme  # http or https
        self.url_netloc = res.netloc
        self.scheduler.insert(start_url)
    def start(self,col = None):
        '''
        启动爬虫，只有爬取完全部数据才会停止
        :param col: mongodb数据的集合对象
        :return:
        '''
        index = 0
        while True:
            url = self.scheduler.get()
            print(url,len(self.scheduler),index )
            index +=1
            if url == None:
                break
            html = BjfuHtmlPage(url)
            #处理网络超时，当网络超时，sleep 1 秒后重新爬取数据
            while True:
                try:
                    html.request()
                    break
                except:
                    print("time out,sleep 1 sec, try again")
                    time.sleep(1)
                    continue

            #提取页面数据，进行存储
            datas = html.get_datas()
            if datas != None and col != None:
                col.insert_one(datas)
            urls,_ = html.get_all_url()
            for url in urls:
                if "http://news.bjfu.edu.cn/lsyw/" in url:
                    self.scheduler.insert(url)

class BjfuHtmlPage(HtmlPage):
    '''
    继承自HtmlPage类，自己实现页面分析get_datas方法就可以
    这是针对绿色新闻网的分析类，可以访问指定url，并对该页面进行分析
    '''
    def __init__(self, url_str, headers_dict=None):
        HtmlPage.__init__(self,url_str, headers_dict)
    def get_datas(self):
        '''
        获取数据，返回dict结构数据，其中包括文章标题，作者，内容等
        主要流程：利用父类的self.soup变量进行页面分析
        :return:
        '''
        title_text = ""
        all_context_text = ""
        publish_time_text = ""
        from_text = ""
        author_text = ""
        click_time_text = ""
        #获取文章内容
        article_con_soup = self.soup.find(attrs={"class": "article_con"})
        if article_con_soup == None:
            return
        context_soup = self.soup.find(attrs={"class": "article_con"}).find_all("p")
        if(len(context_soup) == 0):
            return None
        for context in context_soup:
            context_text = context.get_text()
            if(len(context_text) > 1): #只有一个字符的一般是换行或空格
                all_context_text = all_context_text + context_text + "\n"
        #获取其他项
        other_soup = self.soup.find_all("span")
        for other in other_soup:
            other_text = other.get_text()
            if other_text.find("发表时间：") != -1:
                publish_time_text = re.findall(re.compile(r'[(](.*?)[)]', re.S), other_text)[0]
            elif other_text.find("来源：") != -1:
                from_text = other_text.replace("来源：","")
            elif other_text.find("作者：") != -1:
                author_text = other_text.replace("作者：","")
            # else:
            #     print("#other:",other_text,"#")

        #获取标题
        title_soup = self.soup.find_all("h2")
        if(len(title_soup) > 0):
            title_text = title_soup[0].get_text()
        else:
            title_text = ""
        #获取点击次数
        click_time_url_text = self.soup.find_all("script", attrs={"src":re.compile(r"/cms/web/count.jsp*")})
        if len(click_time_url_text) > 0:
            click_time_url_text = click_time_url_text[0]['src']
            req_click_time = requests.get(self.url_scheme + "://" + self.url_netloc+ click_time_url_text)
            soup_click_time = BeautifulSoup(req_click_time.text, 'html.parser').text
            click_time_text = eval(re.findall(r'[(](.*?)[)]', soup_click_time)[0])  # 获取点击次数结束
        return {"_id": self.url_str, "title":title_text ,"text":all_context_text ,"publishTime":publish_time_text ,"fromText":from_text ,"authon":author_text ,"clickTime":click_time_text}