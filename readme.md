# 北京林业大学绿色新闻搜索引擎

## 整体过程
1. 爬虫爬取以 http://news.bjfu.edu.cn/lsxy/ 打头的所有新闻页面的内容，并将新闻页面的标题（newsTitle）、链接地址(newsUrl)、发表时间(newsPublishTime)、浏览次数(newsClickCount)、来源部门(newsSource)以及新闻内容（newsContent）等属性抓取下来。
2. 关系类数据库不适用于爬虫数据存储，因此使用非关系类数据库MongoDB。数据库可用可视化工具方便查看，例如Mongo Management Studio。
3. 使用Whoosh全文索引库建立文档索引，使用jieba分词引用ChineseAnalyzer进行中文分词,并实现对中文查询提取关键字进行搜索。
4. 搭建人机交互的搜索引擎Web界面。使用flask框架进行HTTP响应

## 使用方法
1. 启动mongodb，并在main.py中的main函数中设置连接mongodb方式，默认是5000端口，数据库无密码， [mongodb安装教程-仅供参考](https://www.runoob.com/mongodb/mongodb-window-install.html)
2. 运行``pip install -r requirements.txt`` 安装依赖库，这里推荐豆瓣的源``-i https://pypi.doubanio.com/simple``
3. 运行mian.py，当第二次运行时可以注释掉main函数，只启动http（main函数的主要功能是爬取数据并保存到数据库）

## 目录结构
```
├─static            网页目录用来存储网页
│  └─css
│  └─js
│  index.html       主页
│  
├─code              python代码文件夹
│  └─baseLib        通用基础类文件夹，用来存放不是针对本工程的通用类
│  BjfuHtml.py      针对本工程的python文件包括GetBjfuHtmls和BjfuHtmlPage连个类
│
└─main.py           主函数
└─requirements.txt
```
## python类介绍
其中基础类是通用类可以用到其他爬虫相关的项目上

### GetBjfuHtmls
- 针对绿色新闻网的爬虫，用一个起始url进行初试化
- 调用start启动爬虫进行连续爬取，知道爬取完全部数据停止
- 主要成员： Scheduler（调度器）
- 若要实现爬取其他网站可以重新实现start方法

### BjfuHtmlPage
- 继承自HtmlPage类，自己实现页面分析get_datas方法就可以
- BjfuHtmlPage是针对绿色新闻网的分析类，可以访问指定url，并对该页面进行分析

### URLList（基础类）
- 一个url容器
- URLList是一个简单的url容器，当url数据量变多时要重新实现URLlist
- 提供增删查三种方法

### Scheduler（基础类）
- 一个简单的调度器，容器采用的URLList
- 只提供两个方法：insert和get，使用者无需关心是否回插入重复的url，也就是说调度器自动避免访问重复的页面
- 同时可以用len方法查看调度器中还有多少url要访问
- 原理：同时有两个容器一个保存要访问的url一个保存历史url,url被get之后会自动从要访问的url容器放入历史容器中

### HtmlPage（基础类）
- HtmlPage:页面分析类，用来对一个页面进行分析
- 使用方式：
    1. 用一个url初试化
    2. 调用request进行请求
    3. 分析页面
    - get_html方法获取整个html（shtring类型）
    - et_all_url方法获取页面中的全部url
    - 子类可以利用self.soup（BeautifulSoup(self.html_text, 'lxml') 的返回）对页面进行分析
    
### MyWhoosh（基础类）
- 对whoosh的简单封装
- 提供增删查3种方法，可以插入一篇文章，然后通过关键字调用find查找这篇文章
