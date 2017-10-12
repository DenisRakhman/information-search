
def normalize_date(date):
    import re
    months = {'январь':'01','февраль':'02','март':'03','апрель':'04','май':'05','июнь':'06','июль':'07','август':'08','сентябрь':'09','октябрь':'10','ноябрь':'11','декабрь':'12'}
    month = months[re.findall('\- (.*?) ', date)[0].lower()]
    day = re.findall(' [(0-9)]*?[snrt]', date)[0]
    year = re.findall(', (.*?) ', date)[0]
    return day+'.'+month+'.'+year


class Article():
    def __init__(self, raw):
        import re
        import urllib.request
        self.author = 'NoName'
        self.link = re.findall('<a href="(.*?)"', raw, flags=re.DOTALL)[0]
        print ('URL: ', self.link)
        self.title = re.findall('rel="bookmark" title="(.*?)"', raw, flags=re.DOTALL)[0]
        self.date = re.findall('"post-date">(.*?)<a', raw, flags=re.DOTALL)[0]
        self.date = normalize_date(self.date)
        self.page = urllib.request.Request(self.link)
        self.page = urllib.request.urlopen(self.page)
        self.page = self.page.read().decode('utf-8')
        self.topic = re.findall('В рубрике.*?<.*?>(.*?)<', self.page, flags=re.DOTALL)[0]
        self.text = re.findall('блока фотографий-->(.*?)<b>Понравилась статья', self.page, flags=re.DOTALL)[0]
        self.text = re.sub('<.*?>', '', self.text)
        self.text = re.sub('&.*?;', '', self.text)

    def save(self):
        file = open('corpus/' + self.title + '.txt', 'w', encoding='utf-8')
        out = '@au ' + self.author + '\n@ti ' + self.title + '\n@da ' + self.date + '\n@topic ' + self.topic + '\n@url ' + self.link + '\n' + self.text
        file.write(out)
        file.close()

class Corpus():
    def __init__(self):
        self.articles = []

    def add_article(self, article):
        self.articles.append(article)

    def create(self, size):
        import urllib.request
        import re
        import os
        file = urllib.request.Request('http://desnyanka.ru/')
        file = urllib.request.urlopen(file)
        filetext = file.read().decode('utf-8')
        months = re.findall('<a href=\'(.*?)\'', re.findall('Архивы.*?<ul>.*?<\/ul>', filetext, flags=re.DOTALL)[0], flags=re.DOTALL)
        #links = re.findall('Архивы.*?<ul>.*?<\/ul>', filetext, flags=re.DOTALL)[0]
        print (months)
        os.makedirs('.\corpus', exist_ok=True)
        number = 0
        for i in range(len(months)):
            if number >= size: break
            cur_month = urllib.request.Request(months[i])
            cur_month = urllib.request.urlopen(cur_month)
            cur_month = cur_month.read().decode('utf-8')
            cur_articles = re.findall('<div class="post-meta".*?<!', cur_month, flags=re.DOTALL)
            #for i in cur_articles:
            #    print(i)
            for art in cur_articles:
                if number >= size: break
                #print (art)
                new = Article(art)
                new.save()
                self.articles.append(new)
                number += 1




import os
os.makedirs('.\corpus', exist_ok=True)
#file = open('.\corpus\dummy.txt','w', encoding='utf-8')
#file.write('helloworld')
c = Corpus()
c.create(100)