import requests
from bs4 import BeautifulSoup
from collections import namedtuple
import re


article = namedtuple("article", ['title', 'url', 'comment'])    # data structure to store article
comment = namedtuple("comment", ["push", 'id', 'content', "ip"])    # data structure to store comment (from article)
usercomment = namedtuple("usercomment", ["push", 'board', 'article', 'content', "ip"])    # data structure to store comment (from same user)


class pttcrawler:
    
    def __init__(self, url_list, article_num):
        
        """function use to init the class
         
        Args:
            param1 (list): list of url of the boards you want to search
            param2 (int): how many article you want to search in a board
        Returns:
            list: list of namedtuple article
        """
        
        self.userdict = dict()
        self.url_list = url_list
        self.article_num = article_num
    
    def start(self):
        
        for url in self.url_list:
            
            article_len = 0
            next_url = url
            
            while article_len < self.article_num:
                
                tmp, next_url = self.getarticle(next_url)
                self.store(tmp)
                article_len += len(tmp)
                
        return self.userdict
        
    def getarticle(self, url):
        
        """function use to get all article from a page
         
        Args:
            param1 (string): url of a page from a board
        Returns:
            list: list of namedtuple article
        """
        
        r = requests.get(
            url = url,
            cookies = {'over18': '1'}
        )
        soup = BeautifulSoup(r.text, "html.parser")
        tmp = list()
        for i in soup.find_all("div", class_="r-ent"):
            try:
                tmp.append(article(i.find("div", class_="title").a.string, \
                                   "https://www.ptt.cc" + i.find("div", class_="title").a['href'],  \
                                   self.getcomment("https://www.ptt.cc" + i.find("div", class_="title").a['href'])))
            except:
                continue
        return tmp, "https://www.ptt.cc" + soup.find("a", string = "‹ 上頁")['href']
    
    
    def getcomment(self, url):
        
        """function use to get all comment from a article
         
        Args:
            param1 (string): url of a article
        Returns:
            list: list of namedtuple comment of that article
        """

        getcontent = lambda i: i.find("span", class_="f3 push-content").string[2:] if not i.find("span", class_="f3 push-content").a \
        else i.find("span", class_="f3 push-content").a['href']
        
        r = requests.get(
            url = url,
            cookies = {'over18': '1'}
        )
        soup = BeautifulSoup(r.text, "html.parser")
        tmp = list()
        for i in soup.find("span", string=re.compile("^※")).find_next_siblings("div", class_="push"):
            try:
                tmp.append(comment(i.find_all("span")[0].string[0], \
                                   i.find_all("span")[1].string, \
                                   getcontent(i), \
                                   i.find_all("span")[3].string.strip().split(" ")[0])
                          )
            except:
                print(i)
        return tmp
    def store(self, ArticleList):
        
        """function use to scan all comment in a list of article and sort them by id
         
        Args:
            param1 (list): list of namedtuple article
        Returns:
            No Return
            
        """
            
        for i in ArticleList:
            for c in i.comment:
                if not c.id in self.userdict.keys():
                    self.userdict[c.id] = [usercomment(c.push, i.url.split("/")[4], i.title, c.content, c.ip)]
                else:
                    self.userdict[c.id].append(usercomment(c.push, i.url.split("/")[4], i.title, c.content, c.ip))
        return    
