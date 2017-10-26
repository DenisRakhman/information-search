
def normalize_date(date):
    import re
    months = {'январь':'01','февраль':'02','март':'03','апрель':'04','май':'05','июнь':'06','июль':'07','август':'08','сентябрь':'09','октябрь':'10','ноябрь':'11','декабрь':'12'}
    month = months[re.findall('\- (.*?) ', date)[0].lower()]
    day = re.findall(' [(0-9)]*?[snrt]', date)[0]
    day = day[:len(day)-1]
    year = re.findall(', (.*?) ', date)[0]
    return day+'.'+month+'.'+year


class Article():
    def __init__(self, raw, parsed = False, lemmatized = False):
        import pymorphy2
        m = pymorphy2.MorphAnalyzer()
        from nltk import word_tokenize
        if parsed == False:
            import re
            import urllib.request
            self.author = 'NoName'
            self.link = re.findall('<a href="(.*?)"', raw, flags=re.DOTALL)[0]
            #print ('URL: ', self.link)
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
        else:
            import re
            self.author = re.findall('@au (.*?)\n', raw)[0]
            self.title = re.findall('@ti (.*?)\n', raw)[0]
            self.link = re.findall('@url (.*?)\n', raw)[0]
            self.topic = re.findall('@topic (.*?)\n', raw)[0]
            self.date = re.findall('@da (.*?)\n', raw)[0]
            self.text = re.findall('@url.*?\n(.*)', raw, flags=re.DOTALL)[0]
        if lemmatized == False:
            self.bol = ([m.parse(w)[0].normal_form for w in word_tokenize(self.text) if m.parse(w)[0].tag.POS not in ['PREP', 'CONJ', 'PRCL']])
        else:
            file = open('.\lem_corpus\\'+self.title+'.txt', 'r', encoding='utf-8')
            lemmas = file.read()
            self.bol = lemmas.split()
            file.close()

    def save(self):
        file = open('corpus/' + self.title + '.txt', 'w', encoding='utf-8')
        out = '@au ' + self.author + '\n@ti ' + self.title + '\n@da ' + self.date + '\n@topic ' + self.topic + '\n@url ' + self.link + '\n' + self.text
        file.write(out)
        file.close()

    def __repr__(self):
        return self.title

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
        #print (months)
        os.makedirs('.\corpus', exist_ok=True)
        number = 0
        for i in range(len(months)):
            if number >= size: break
            cur_month = urllib.request.Request(months[i])
            cur_month = urllib.request.urlopen(cur_month)
            cur_month = cur_month.read().decode('utf-8')
            cur_articles = re.findall('<div class="post-meta".*?<!', cur_month, flags=re.DOTALL)
            for art in cur_articles:
                try:
                    if number >= size: break
                    new = Article(art)
                    new.save()
                    self.articles.append(new)
                    number += 1
                except:
                    pass

    def lemmatize(self):
        import os
        os.makedirs('.\lem_corpus', exist_ok=True)
        for a in self.articles:
            file = open('.\lem_corpus\\' + a.title + '.txt', 'w', encoding='utf-8')
            file.write(' '.join(a.bol))
            file.close()

    def clean(self):
        import os
        for root, dirs, files in os.walk('.\corpus'):
            for file in files:
                if file[len(file)-3: len(file)] != 'txt':
                    os.remove('.\corpus\\'+file)
        for root, dirs, files in os.walk('.\lem_corpus'):
            for file in files:
                if file[len(file)-3: len(file)] != 'txt':
                    os.remove('.\lem_corpus\\'+file)

    def open(self):
        import os
        for root, dirs, files in os.walk('.\corpus'):
            for file in files:
                if file[len(file)-3: len(file)] == 'txt':
                    newf = open('.\corpus\\'+file, 'r', encoding='utf-8')
                    new = newf.read()
                    self.articles.append(Article(new, parsed=True, lemmatized=True))
                    newf.close()
                else:
                    pass
                    #print ('empty')

    def delete(self):
        import os
        for root, dirs, files in os.walk('./corpus'):
            for f in files:
                print (f)
                try:
                    os.remove('./corpus/' + f)
                except:

                    print ('no')
        for root, dirs, files in os.walk('./lem_corpus'):
            for f in files:
                os.remove('./lem_corpus/' + f)
        for i in range(0,1):
            try:
                os.remove('ii_list.txt')
            except:
                pass

    def get_matrix(self, save = True):
        #print ('aaaa')
        import collections as cl
        import pymorphy2
        m = pymorphy2.MorphAnalyzer()
        corp = [a.bol for a in self.articles]
        banlist = [' ', ',', '\ufeff', '.', ':', ';', '?', '!']
        mtx = cl.defaultdict()
        for num in range(len(corp)):
            #print ('aa')
            #print (corp[num][:15])
            text = (corp[num])
            for word in text:
                if word not in banlist and '\n' not in word:
                    if word not in mtx:
                        mtx[word] = []
                    if str(num) not in mtx[word]:
                        mtx[word].append(str(num))
        if save == True:
            file = open('ii_list.txt', 'w', encoding='utf-8')
            out = '\n'.join([w + ' - ' + ', '.join(mtx[w]) for w in mtx])
            file.write(out)
            file.close()
        return mtx

    def compute_K(self, dl, avdl):
        k1 = 2.0
        b = 0.75
        return k1 * ((1 - b) + b * (float(dl) / float(avdl)))

    def score_BM25(self, n, fq, N, dl, avdl):
        from math import log

        k1 = 2.0
        b = 0.75
        K = self.compute_K(dl, avdl)
        IDF = log((N - n + 0.5) / (n + 0.5))
        if IDF < 0:
            #print (IDF, N, n)
            pass
        frac = ((k1 + 1) * fq) / (K + fq)
        return IDF * frac



    def request(self, req):
        from nltk import word_tokenize
        import os
        import pymorphy2
        import collections as cl
        m = pymorphy2.MorphAnalyzer()
        for i in range (0, 1):
            try:
                file = open ('ii_list.txt', 'r', encoding='utf-8')
            except:
                self.get_matrix()
                file = open ('ii_list.txt', 'r', encoding='utf-8')
        ii_list_t = file.read()
        file.close()
        ii_list = {}
        req = word_tokenize(req)
        req = [w.strip('!?.,:;-"') for w in req]
        req = [m.parse(w)[0].normal_form for w in req if m.parse(w)[0].tag.POS not in ['PREP', 'CONJ', 'PRCL'] and m.parse(w)[0].normal_form != '']
        N = len(self.articles)
        avdl = sum([len(a.bol) for a in self.articles])/N
        for l in ii_list_t.split('\n'):
            new = l.split(' - ')
            ii_list[new[0]] = new[1]
        candidates = []
        for q in req:
            if q in ii_list:
                candidates.extend([self.articles[int(num)] for num in ii_list[q].split(', ')])
        n = len(candidates)
        score = {}
        for c in candidates:
            curscore = 0
            for q in req:
                fq = len([w for w in c.bol if w == q])/len(c.bol)
                newscore = self.score_BM25(len(ii_list[q].split(', ')), fq, N, len(c.bol), avdl)
                if newscore > 0:
                    curscore += newscore
            score[c] = curscore
        score = cl.OrderedDict(sorted(score.items(), key=lambda t: t[1], reverse=True))
        print(score)
        return score

#c = Corpus()
#c.create(6)

#c.lemmatize()

#c.clean()
#c.open()
#c.get_matrix()
#c.request('рыба')