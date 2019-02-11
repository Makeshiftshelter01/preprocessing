from pymongo import MongoClient
import pandas as pd
#from konlpy.tag import Okt
from ckonlpy.tag import Twitter
import os
import re

print(os.getcwd())

client = MongoClient('mongodb://13.125.221.134:9046')
db = client.mongodb
# 컬렉션 객체 가져오기
# ilbe_coll = db['cleaned_ilbe']
coll = db['realnavernews']

twitter = Twitter()

#keyword = '회담'



cursor = coll.find({}).sort([('_id', -1)])

def news_check():
        for text in cursor:
                yield text
                
                
                
gen = news_check()
                
while True:         

        text = next(gen)

        precontent = text['content']['ccontent']

        precontent = re.sub('// flash.*\{\}', '', precontent)
        
        precontent = twitter.morphs(precontent)
        
        
        #cursor = coll.find({'cno' : {'$regex' : keyword}}).limit(1)
        data = pd.read_csv('SentiWord_Dict2.txt', sep='\t', header=None)

        words = list(data.iloc[:, 0])
        score = list(data.iloc[:, 1])

        #content = content.split(' ')
        content = []

        for i in range(len(precontent)):
                if len(precontent[i]) >= 2:
                        content.append(precontent[i])

        print('제목: ',text['ctitle'])
        print('언론사: ',text['content']['news_company'])
        print(' '.join(content))
        print()
        scores = 0
        temp = []

        for i in range(len(content)):
                for j in range(len(words)):
                        if content[i] == words[j]:
                        #print(content[i],'==', words[j], score[j])
                                temp.append(content[i])   
                                scores = scores + int(score[j])

        notin = []
        for i in range(len(content)):
                if content[i] not in temp:
                        notin.append(content[i])

        print('=-=-=-=-=-= 포함되지 못한 단어 =-=-=-=-=-=-=-=')

        notin = list(set(notin))

        for i in range(len(notin)):
                print(notin[i], end='\t')

        

        print()
        print('점수:',scores)
        print()

        put = input('=-=-=-=-=종료하려면 exit 입력, 계속하려면 아무 키=-=-=-=-=')
        print()
        put

        if put == 'exit':
                exit()
        else: pass
