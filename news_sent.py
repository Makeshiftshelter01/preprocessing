from pymongo import MongoClient
import pandas as pd
#from konlpy.tag import Okt
from ckonlpy.tag import Twitter
from collections import Counter
import os
import re

print(os.getcwd())

client = MongoClient('mongodb://13.125.221.134:9046')
db = client.mongodb
# 컬렉션 객체 가져오기
# ilbe_coll = db['cleaned_ilbe']
coll = db['realnavernews']

twitter = Twitter()

keyword = '회담'


#cursor = coll.find({'cno' : {'$regex' : keyword}}).limit(1)


cursor = coll.find({}).sort([('_id', 1)])


def news_check():
    for text in cursor:
        yield text
            
                
                
gen = news_check()


stopword_dict = {}

try:
    cnt = int(input('시작 번호를 입력하세요 (1~5965)'))
    if cnt > 1 and cnt < 5966:
        for i in range(cnt):
            text = next(gen)
    elif cnt == 1 or cnt <= 0:
        cnt = 1
        text = next(gen)
    elif cnt >= 5966:
        print('!!!마지막 번호는 5965입니다')
        exit(0)
except:
    print('알맞은 숫자를 입력하세요. 프로그램 종료!')
    exit()

while True:     
    precontent = text['content']['ccontent']
    precontent = re.sub('// flash.*\{\}', '', precontent)
    
    precontent = twitter.morphs(precontent)

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

    print('***현재 번호 : ', cnt)
    print('=-=-=-=-=-= 포함되지 못한 단어 =-=-=-=-=-=-=-=')

    notin = list(set(notin))

    # 지속해서 나오는 의미없는 단어들은 필터링

    with open('news_stopwords.txt', 'r',  encoding='utf-8') as f:
        stopwords = f.readlines()

    stopwords = [line[:-1] for line in stopwords]
  
    for i in range(len(notin)):
        if notin[i] not in stopword_dict:
            stopword_dict[notin[i]] = 0

        stopword_dict[notin[i]] += 1
    
    stopword_keys = list(stopword_dict.keys())
    stopword_values = list(stopword_dict.values())

    stopword_add = []
    for i in range(len(stopword_keys)):
        if stopword_values[i] > 3 and stopword_keys[i] not in stopwords:
            stopword_add.append(stopword_keys[i])
            stopword_dict.pop(stopword_keys[i])

    f = open('news_stopwords.txt', 'a', encoding='utf-8', newline='\n')
    for i in range(len(stopword_add)):
        dt = '%s\n' % (stopword_add[i])
        f.write(dt)
    
    f.close()
        
    with open('news_stopwords.txt', 'r',  encoding='utf-8') as f:
        stopwords = f.readlines()

    stopwords = [line[:-1] for line in stopwords]
  

    for i in range(len(notin)):
        if notin[i] not in stopwords:
            print(notin[i], end='\t')

  
    print('\n\n')
    
    print('점수:',scores)
    print()


    print('종료 : 종료 / 다음 글 : 다음 / 감정 사전 업데이트 : 단어1,점수1(띄어쓰기)단어2,점수2(띄어쓰기)...')
    print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')

    while True:     
        put = input('명령어 입력 : ')
        put

        if put == '종료' or put.lower() == 'exit':
            print('종료합니다')
            exit()
        elif put == '다음' or put.lower() == 'pass':
            break
        else:
            try:
                f = open('SentiWord_Dict2.txt', 'a', encoding='utf-8', newline='\n')
                wd_set = put.split(' ')
                for wd in wd_set:
                    wd = wd.split(',')

                    if len(wd) > 2:
                        print()
                        print('새로운 단어는 띄어쓰기로 구분해주세요!!!')
                        print('***다음 단어는 추가되지 않습니다: %s' % (wd[0]))
                        continue
                    
                    f.write('\n%s\t%s' % (wd[0], int(wd[1])))
                f.close()
                
                print()
                print('단어 추가 작업 완료')
            except:
                print('오타가 있는 것 같습니다. 다시 입력해주세요')
                pass
    
    # 다음으로 진행
    cnt += 1

    if cnt >= 5966:
        print('모든 기사 조회 완료. 프로그램 종료!')
        exit()
    text = next(gen)