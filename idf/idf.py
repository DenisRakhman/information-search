import pymystem3
import collections as cl
import os
ms = pymystem3.Mystem()

def get_matrix(corpus):
    banlist = [' ', ',', '\ufeff', '.', ':', ';', '?', '!']
    mtx = cl.defaultdict()
    for num in range(len(corpus)):
        text = ms.lemmatize(corpus[num])
        for word in text:
            if word not in banlist and '\n' not in word:
                if word not in mtx:
                    mtx[word] = []
                mtx[word].append(str(num+1))
    return mtx

corpus = []
for root, dir, files in os.walk('./tests'):
    for file in files:
        newfile = open('./tests/'+file, 'r', encoding='utf-8')
        corpus.append (newfile.read())
        newfile.close()

out =  get_matrix(corpus)
print(out)
file = open('idf.txt', 'w', encoding='utf-8')
text = ''
for word in out:
    text += word +' - ' + ','.join(out[word]) +'\n'
file.write(text)
file.close()
