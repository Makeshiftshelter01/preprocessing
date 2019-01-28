# -*- encoding: utf-8 -*-
from ruri_dao import CrwalingDAO
from get_element import getElement
from ruri_connect import ConnectTo
import collections
import bson
from bson.codec_options import CodecOptions
import re
import os
import platform
from configparser import ConfigParser
from datetime import datetime
import math
from time import sleep
# from konlpy.tag import Okt
from ckonlpy.tag import Twitter as Okt
import json
from collections import OrderedDict
import psutil



class first:
    def __init__(self,collection, start, many,feature=''):
        self.collection = collection
        self.many = many
        self.start = start
        self.feature = feature

    def bringgd(self):
        cd = CrwalingDAO()
        result = cd.select(self.collection, self.start, self.many)
        gd = getElement(result)  
        return gd

    def temp(self, ilbe, inven,cook,ruri,fmkorea,clien,womad,theqoo,mlbpark,ygosu): 
        ilbe = ilbe
        inven = inven
        cook = cook
        ruri = ruri
        fmkorea = fmkorea
        clien = clien
        womad = womad
        theqoo = theqoo
        mlbpark = mlbpark
        ygosu = ygosu
        return ilbe,inven,cook,ruri,fmkorea,clien,womad,theqoo,mlbpark,ygosu

# 전처리 class
class cleaner:
    def __init__(self, gd, feature, listname, collection, labels=None):
        self.gd = gd
        self.feature = feature
        self.listname = listname
        self.collection = collection 
        self.labels = labels


    # 시간과 추천을 제외한 전처리 패턴과 전처리를 관리하는 함수
    def substr_with_patterns(self, list2string):
        oripatterns = [
            r'[A-Za-z\(\)\·\<\>ㄱ-ㅎ]+',
            r'\s\d\w',
            r'ㅠ|ㅜ|ㅡ|ㅗ|ㅇ|ㅎ|ㅋ|ㅉ|ㅁ|ㅈ',
            r'[\t\xa0]*'
        ]
        #    r'╰( ´•ω•)つ──☆ °.*•。',
        #    r'[A-Z|a-z|0-9|ㅗㅠㅡㅜ]*',
        #    r'[ㄱ-ㅎ|ㅏ-ㅣ]*',
        #    r'\d+[가-힣]',
        #    r'[A-Z|a-z]*\\\\',
        #    r'(.)\1{5,}',
        #     '[^\x00-\x7F\uAC00-\uD7AF]'
        
      
        patterns = oripatterns # 전처리 할 특수기호를 다양하게 조정하기 위해 변수에 저장

        
        
        list2string = list2string # 전처리 할 텍스트
        terror = []

    
        # 링크의 경우
        if self.feature == self.gd.clinks:
            linkpatterns = r'[\!\?\/\★\$\&\@\%\~\[\]\(\)\{\}\,\=\+\-\_\:\;\*\^]'
            patterns[0] = linkpatterns
        # 그 외 콘텐트, 타이틀 등 나머지 항목의 경우
        else:
            linkpatterns = r'[ \!\?\★\$\&\@\%\~\[\]\(\)\{\}\,\=\+\-\_\:\;\*\^\\ud83d]'
            patterns[0] = linkpatterns
        
        # 패턴 전처리 (알 수 없는 패턴이 발견될 경우 error가 발생하기 때문에 try)
        for pattern in patterns:
            try:
                list2string = re.sub(pattern, '', list2string)
                list2string = re.sub(r'[\n]', ' ', list2string)
                list2string = re.sub(r'(\.)+', ' ', list2string)
                list2string = re.sub(r'\d+[가-힣]', ' ', list2string)
                list2string = re.sub(r'[0-9A-Za-z]', ' ', list2string)
                list2string = re.sub(r'[ \★\$\&\@\[\]\(\)\{\}\,\=\+\-\_\:\;\*\^\\ud83d]', ' ', list2string)
                list2string = re.sub(r'[\?\%\!\#\"\-\&\~\^\/\>]', ' ', list2string)
               # list2string = re.sub(r'[\.]', ' ', list2string)
                list2string = re.sub('[^\x00-\x7F\uAC00-\uD7AF]', ' ', list2string)
                
            except TypeError as e:
                terror.append(e)
                print('익셉션에서 처리 : ', e) 
        if len(terror) > 0:
            print('contents 에러개수\n',len(terror))
        return list2string
        
    # 시간과 추천을 제외한 전처리
    def substr_common(self, onegd):
        innerlist = []
        cleaned = None
        
        for i in range(len(onegd)):
            if type(onegd[i]) == str:
                list2string = onegd[i]
                cleaned = self.substr_with_patterns(list2string)
                innerlist.append(cleaned)
            else:
                list2string = ','.join(onegd[i])
                cleaned = self.substr_with_patterns(list2string)
                innerlist.append(cleaned.split(','))
        return innerlist


    # 댓글 전처리
    def substr_reply(self, onegd):
        innerlist = []
        cleaned = None
        
        for i in range(len(onegd)):
            if type(onegd[i]) == str:
                list2string = onegd[i]
                cleaned = self.substr_with_patterns(list2string)
                innerlist.append(cleaned)
            else:   
                innerlist0 = []
                for j in range(len(onegd[i])):    
                    list2string = ','.join(onegd[i][j])
                    cleaned = self.substr_with_patterns(list2string)
                    innerlist0.append(cleaned)
                innerlist.append(innerlist0)
            
        return innerlist

        
    
    # 시간 전처리 1단계 - 날짜 텍스트만을 남기는 전처리.
    def substr_time_lv1(self, i, rawdata, gdidate, collection, labels):
        # labels => [ilbe, inven, cook, ruri, fmkorea, clien]
      
        rawdata = gdidate[i] # 날짜가 포함된 텍스트를 rawdata 변수에 넣기
        cleaned = None #전처리 된 텍스트를 저장할 clean 변수 선언
                    
        # 텍스트를 str로 만들필요 없는 데이터의 경우 - (82쿡, 클리앙)
        if collection == labels[2] or collection == labels[5]:
            if type(rawdata) == list:
                cleaned = rawdata[0]
            else:    
                cleaned = rawdata

        # 텍스트를 str로 만들필요 있는 데이터의 경우 - (루리웹, 일베, 에프엠코리아, 인벤)
        else:
            rawdata = str(rawdata)
            if collection == 'realcook' or collection == 'ruri':
                cleaned = re.sub(r'[\(\)]*','', rawdata) #루리웹
            else:
                cleaned = rawdata
        
        cleaned = re.sub(r'[\t\r\n\xa0]*','', cleaned)
        return cleaned

    # 시간 전처리 2단계 - 날짜 텍스트의 전처리
    def substr_time_lv2(self, cleaned, gdidate, collection, labels):
        cleaned = cleaned
        toDatetype = None
        # labels => [ilbe, inven, cook, ruri, fmkorea, clien]
        
        # 82쿡
        if collection == labels[2]: 
            cleaned =re.sub('[작성일:]','', cleaned)
            cleaned =cleaned.lstrip()
            toDatetype = datetime.strptime(cleaned, '%Y-%m-%d %H%M%S')

        # clien
        elif collection == labels[5]: 
            cleaned =re.sub('수정일 : 2018-06-20 16:57:03','', cleaned)
            cleaned =cleaned.lstrip()
            cleaned =cleaned[:19]
            toDatetype = datetime.strptime(cleaned, '%Y-%m-%d %H:%M:%S')
        
        # ygosu
        elif collection == labels[9]: 
            cleaned =re.sub('DATE :','', cleaned)
            cleaned =cleaned.lstrip()
            cleaned =cleaned[:19]
            toDatetype = datetime.strptime(cleaned, '%Y-%m-%d %H:%M:%S')

        # ruriweb, womad
        elif collection == labels[3] or collection == labels[6]:
            cleaned = cleaned.lstrip()
            if collection == labels[3]:
                toDatetype = datetime.strptime(cleaned, '%Y.%m.%d %H:%M:%S')
            elif collection == labels[6]:
                toDatetype = datetime.strptime(cleaned, '%Y-%m-%d %H:%M:%S')


        # fmkorea,mlbpark,inven
        elif collection == labels[4] or collection == labels[8] or collection == labels[1]:
            cleaned = cleaned.lstrip()
            cleaned = cleaned +':00'
            if collection == labels[4]:
                toDatetype = datetime.strptime(cleaned, '%Y.%m.%d %H:%M:%S')
            elif collection == labels[8] or collection == labels[1]:
                toDatetype = datetime.strptime(cleaned, '%Y-%m-%d %H:%M:%S')
        # ilbe
        else:
            cleaned = cleaned.lstrip()
            cleaned = cleaned[:11]
            cleaned = cleaned +' 00:00:00'
            toDatetype = datetime.strptime(cleaned , '%Y.%m.%d %H:%M:%S')
           
        
        return toDatetype

    # 시간 전처리 (복잡한 부분은 1, 2단계 함수로 분리)
    def substr_time(self, gdidate, collection, labels):
        # 변수
        gdidate = gdidate
        idate = []
        cnterror = [] # 에러
        
        for i in range(len(gdidate)):
            # 시간
            try:
                rawdata = None
                cleaned = None
                toDatetype = None
                
                # 빈칸이나 에러가 아닐 경우에만 전처리 시작
                if gdidate[i] != 'fillblanks' and gdidate[i] != 'errorpassed':
                    # level 1 - 날짜 텍스트만 남기는 전처리
                    cleaned = self.substr_time_lv1(i, rawdata, gdidate, collection, labels)

                    # level 2 - 날짜 텍스트의 전처리
                    toDatetype = self.substr_time_lv2(cleaned, gdidate, collection, labels)
                    
                    # level 3 - Date 변환
                    idate.append(toDatetype)
                
                # 빈칸이나 에러의 경우 전처리 없이 그냥 리스트에 넣기
                else:
                    idate.append(toDatetype)

            # 시간 예외처리
            except ValueError as e:
                idate.append(gdidate[i])
                cnterror.append(e)
                print('date에러 상세 사항\n:', e)
        print('date에러개수',len(cnterror))
        
        return idate
        
    # 모든 추천 종류 전처리
    def thumb(self, thumblist):
        # 변수
        listname = []
        pattern = None
        # thumbupl일 경우 다른패턴 적용 
        if thumblist == self.gd.cthumbupl:
            pattern = r'[\t\r\n]*'
        else:
            pattern = r'[\t\r\n\s]*'

        # 실행
        for thumbone in thumblist:
            rawdata = thumbone
            if isinstance(rawdata, str):
                rawdata = str(rawdata) # thumbupl의 rawdata를 스트링으로
            
            cleaned =re.sub(pattern,'', rawdata)       
            listname.append(cleaned)
        return listname

    # feature : gd.title, gd.content 등
    def cleaning(self):
        # date 전처리
        if self.feature == self.gd.idate:
            self.listname = self.substr_time(self.feature, self.collection, self.labels)

        # thumbup, cthumbdownl, cthumbupl 전처리
        elif self.feature == self.gd.thumbup or self.feature == self.gd.cthumbdownl or self.feature == self.gd.cthumbupl:
            self.listname = self.thumb(self.feature)           
        
        # 댓글
        elif self.feature == self.gd.creplies:
            self.listname = self.substr_reply(self.feature)
       
        
        #  링크, 콘텐츠, 타이틀 등 나머지 항목 전처리               
        else:
            self.listname = self.substr_common(self.feature)

        return self.listname

## 토큰화를 위한 클래스 선언
class tokenizer:
   def token(self, title, ccontent, creplies):
       memory = psutil.Process(os.getpid())

       T_OR_title = []
       T_title = []
       T_OR_ccontent = []
       T_ccontent = []
       T_OR_creplies = []
       T_creplies = []
      
       twitter = Okt()   # 트위터 형태소 사전을 사용하기 위해 초기화
       twitter.add_dictionary('백래시', 'Noun')
       twitter.add_dictionary('문재앙', 'Noun')

       #### 타이틀 토큰화 
       #print('1')    
       for i in range(len(title)):
           
           a = twitter.pos(title[i])
           b = []
           #print('title[i]',i,title[i])    
           for j in range(len(a)):
               if a[j][1] != 'Punctuation':   # 오류로 'Punctuation'에 해당하는 튜플 제거 
                   b.append(a[j])
                   #print('3',j)
           T_OR_title.append(b)
           T_title.append(twitter.morphs(title[i]))
          
          
           #### ccontent 토큰화
           try:    
               c = twitter.pos(str(ccontent[i]))
               d = []
              # print('ccontent[i]',i, ccontent[i])
               for w in range(len(c)):     
                   if c[w][1] != 'Punctuation':  # 오류로 'Punctuation'에 해당하는 튜플 제거
                       d.append(c[w])
                       #print('4',w)
               T_OR_ccontent.append(d)
               T_ccontent.append(twitter.morphs(str(ccontent[i])))


           except RuntimeError as e:
               T_OR_ccontent.append('')
               T_ccontent.append(twitter.morphs(''))

           ### 댓글 토큰화
           #print('creplies[i]',i,creplies[i])
        
           if type(creplies[i]) == str:    # string형 댓글 토큰화
               a = [creplies[i]]           # string을 리스트로 변경
               e = twitter.pos(str(a))
               f = []
               for u in range(len(e)):
                   if e[u][1] != 'Punctuation':
                       f.append(e[u])
                   elif e[u][1] != 'KoreanParticle':
                       f.append(e[u])  
                   else:
                       break  
                   #print('5',u)
               T_OR_creplies.append(f)
               T_OR_creplies.append(twitter.pos(str(a)))
               T_creplies.append(twitter.morphs(str(a)))
              
           else:
               temp = []
               temp2 = []
         
               x = []

               for n in range(len(creplies[i])):   ### 리스트로 반환되는 댓글
                   h = twitter.pos(creplies[i][n])
                   #print('6',n)

                   for z in range(len(h)):
                       if h[z][1] != 'Punctuation':
                           x.append(h[z]) 
                       elif h[z][1] != 'KoreanParticle':
                           x.append(h[z])
                       else:
                           break  
                      # print('7',z)
                      # print('8',)
                       #print('h',z,h)
              
                   temp.append(x)
                   temp2.append(twitter.morphs(creplies[i][n]))
               
               T_OR_creplies.append(temp)
               T_creplies.append(temp2)
              
       return  T_OR_title, T_title, T_OR_ccontent, T_ccontent, T_OR_creplies, T_creplies

## 품사를 나누어줄 분류기 선언
class classifier:
   def classify(self, token):
       T_OR_title = token[0]
       T_OR_ccontent = token[2]
       T_OR_creplies = token[4]

       T_adjective = []
       T_adverb = []
       T_verb = []
       T_nouns = []



       sumup = []   # 타이틀 내용 댓글을 한번에 모을 리스트 필요
       for k in range(len(T_OR_title)):
           token = T_OR_title[k] + list(T_OR_ccontent[k])   # 타이틀 내용

           reply = []
          
           for j in range(len(T_OR_creplies[k])):  # 댓글
               if type(T_OR_creplies[k][j]) == 'tuple':   
                   reply.extend(T_OR_creplies[k][j])
               else:
                   reply.extend([('님', 'Suffix')]) 
                   ## 튜플로 반환되지 않는 경우는 임의로 튜플형으로 만들어 반환    
           token.extend(reply)
           sumup.append(token)
              
       ##### 'Adjective' 추출         
       for i in range(len(sumup)):
           temp2 = []      
           for j in range(len(sumup[i])):
               temp = []
               if sumup[i][j][1] == 'Adjective' :                   
                   temp.append(sumup[i][j][0])
               if len(temp) != 0: 
                   temp2.extend(temp)                                
           T_adjective.append(temp2)   
      
       ##### 'Adverb' 추출        
       for i in range(len(sumup)):
           temp2 = []      
           for j in range(len(sumup[i])):
               temp = []
               if sumup[i][j][1] == 'Adverb' :
                   temp.append(sumup[i][j][0])    
               if len(temp) != 0: 
                   temp2.extend(temp)

           T_adverb.append(temp2)   
      

       ##### 'Verb' 추출        
       for i in range(len(sumup)):
           temp2 = []      
           for j in range(len(sumup[i])):
               temp = []
               if sumup[i][j][1] == 'Verb' :
                   temp.append(sumup[i][j][0])  
               if len(temp) != 0: 
                   temp2.extend(temp)

           T_verb.append(temp2)  

       ##### 'Noun' 추출        
       for i in range(len(sumup)):
           temp2 = []      
           for j in range(len(sumup[i])):
               temp = []
               if sumup[i][j][1] == 'Noun' :
                   temp.append(sumup[i][j][0])   
               if len(temp) != 0: 
                   temp2.extend(temp)
          
           T_nouns.append(temp2)
       return T_adjective, T_adverb, T_verb, T_nouns
          





class config_for_update:

    def __init__(self, configFilename = 'config.1.ini', debug = False):
        
        self.debug = debug

        # 상대경로
        self.filename = os.path.join(os.path.relpath(os.path.dirname(__file__)), configFilename)
        
        self.config = ConfigParser()
        self.parser = self.config.read(self.filename, encoding='utf-8')
        print("Load Config : %s" % self.filename)



            # config to dict
    def as_dict(self, config):
        the_dict = {}
        for section in config.sections():
            the_dict[section] = {}
            for key, val in config.items(section):
                the_dict[section][key] = val
        
        return the_dict
        #ini 파일에서 전체 및 특정 자료 찾기
    def read_info_in_config(self, section=None):
        config = self.config
        cdict = self.as_dict(config)
        print(type(cdict[section]))
        if section == None:
            return cdict
        else:
            return cdict[section]

    def get_coll_dict(self, target, db ='mongoDB'):
        config = self.config
        coll_dict = {}
        for key, value in config.items(db):
            coll_dict[key]= value
        coll_dict['collection'] = target
        return coll_dict

# 몽고디비 연결 -> 전처리한 데이터를 새 collection에 담는 작업을 실행할 update_db 클래스 선언
class update_db:
    
    def setdbinfo(self):
        host = "" # linux구분
        if platform.system() != "Linux":
            host = 'host'
        else:
            host = 'host'

        # ini파일을 이용해 접속 데이터 읽기
        config = config_for_update()
        data = config.read_info_in_config('mongoDB')
        cnct = ConnectTo(data[host],int(data['port']),data['database'],data['collection']) #인스턴스화
        cnct.MongoDB() #mongoDB 접속, 현재는 mongoDB만 가능하지만 추후 다른 DB도 선택할 수 있도록 변경
        return cnct


    def insertone(self, gd, title, ccontent, idate, clinks, creplies, token, pos):
        #token => [T_OR_title, T_title, T_OR_ccontent, T_ccontent, T_OR_creplies, T_creplies]
        #pos => [T_adjective, T_adverb, T_verb, T_nouns]
        
        config = config_for_update()
        conn = self.setdbinfo()


        # 몽고DB에 입력
        for i in range(len(gd.id)):
            mongoDict = {}
            #mongoDict['id'] = gd.id[i] #db 입력시 새로운 id 생성되므로 이 부분은 업데이트하지 않음
            mongoDict['cno'] = gd.no[i]
            mongoDict['clink'] = gd.html[i]
            mongoDict['ctitle'] = title[i]
            mongoDict['cthumbup'] = gd.thumbup[i]
            mongoDict['cthumbdown'] = gd.thumbdown[i]

            mongoDict['content'] = {}
            mongoDict['content']['ccontent'] = ccontent[i]
            mongoDict['content']['cthumbupl'] = gd.cthumbupl[i]
            mongoDict['content']['cthumbdownl'] = gd.cthumbdownl[i]
            mongoDict['content']['idate'] = idate[i]
            mongoDict['content']['news_company'] = gd.news_company[i]
            mongoDict['content']['clinks'] = clinks[i]
            mongoDict['content']['creplies'] = creplies[i]

            mongoDict['tokenized'] = {}
            mongoDict['tokenized']['T_title'] = token[1][i] #T_title[i]
            mongoDict['tokenized']['T_ccontent'] = token[3][i] #T_ccontent[i]
            mongoDict['tokenized']['T_creplies'] = token[5][i] #T_creplies[i]
            mongoDict['tokenized']['T_noun'] =  pos[3][i] #T_nouns[i]
            mongoDict['tokenized']['T_adjective'] = pos[0][i]  #T_adjective[i]
            mongoDict['tokenized']['T_adverb'] = pos[1][i] #T_adverb[i]
            mongoDict['tokenized']['T_verb'] = pos[2][i] #T_verb[i]

            try:
                doc_id = conn.m_collection.insert_one(mongoDict).inserted_id
            except UnicodeEncodeError as e:
                print('이모지애러',e)
            print('no.', i+1, 'inserted id in mongodb : ', doc_id)

        conn.m_client.close()

    def make_json(self, filename2,gd, title, ccontent, idate, clinks, creplies, token, pos):
        self.filename2 = filename2
        for i in range(len(gd.id)):
            jsonfile = OrderedDict()
            jsonfile['cno'] = gd.no[i]
            jsonfile['clink'] = gd.html[i]
            jsonfile['ctitle'] = title[i]
            jsonfile['cthumbup'] = gd.thumbup[i]
            jsonfile['cthumbdown'] = gd.thumbdown[i]
            jsonfile['content'] = {'ccontent':ccontent[i],'cthumbupl':gd.cthumbupl[i],'cthumbdownl':gd.cthumbdownl[i],
                'idate':str(idate[i]), 'news_company': gd.news_company[i],'clinks':clinks[i],'creplies':creplies[i]}
            jsonfile['tokenized'] = {'T_title':token[1][i],'T_ccontent':token[3][i],'T_creplies':token[5][i],
                'T_noun':pos[3][i], 'T_adjective':pos[0][i],'T_adverb':pos[1][i],'T_verb':pos[2][i]}
        
            with open(self.filename2,'a', encoding="utf-8") as make_file:
                json.dump(jsonfile, make_file, ensure_ascii=False,indent='\t')
        print(self.filename2, 'json파일 다운로드')