from navernews01 import first
from navernews01 import cleaner
from navernews01 import tokenizer
from navernews01 import classifier
from navernews01 import update_db
import time 
from konlpy.tag import Okt
from ckonlpy.tag import Twitter as Okt
import re
import psutil
import os


timehisory = []
memory = []

process = psutil.Process(os.getpid())   # 메모리 확인용
mem_before = process.memory_info().rss / 1024 / 1024

# 시작 전 ini 파일에서 collection 설정할 것!!!

total = 1000
for i in range(0,59):
    startime = time.time()
    
    # 값 설정
    start = total*i
    ##### 전처리하고자하는 콜랙션 이름을 넣으시오 collectionname, first, newdata.temp
    # realcook 103까지 토큰화 104 토큰화 시작해야함 100개씩
    collectionname =  'realnavernews'   
    newdata = first('realnavernews',start, total)  # start 부터 1000개씩 DB로부터 가져오기
  
    # 데이터 가져오기
    gd = newdata.bringgd()

    # 전처리된 데이터를 담을 리스트 준비(제목, 내용, 댓글말 전처리할 예정)
    cno = []
    title = []
    thumbup = []
    cthumbdownl = []
    cthumbupl = []
    ccontent = []
    creplies = []
    clinks = [] 
    idate = []

    # 주제 전처리
    no  = gd.no

    # 내용 전처리 
    new_ccontent = cleaner(gd, gd.ccontent, ccontent,collectionname)
    ccontent = new_ccontent.cleaning()

    # 타이틀 전처리
    new_title = cleaner(gd, gd.title, title,collectionname)
    title = new_title.cleaning()


    # 토큰화
    print(i,'번째 루프 토큰화 시작')
    tk = tokenizer()
    token = tk.token(no, title, ccontent) # 순서대로 return T_OR_title, T_title, T_OR_ccontent, T_ccontent, T_OR_creplies, T_creplies
    # token변수만 메모리를 쓰도록 다른 변수를 선언하지 않는다.



    # 품사 나눔
    print(i,'번째 루프 품사나눔')
    clf = classifier()
    pos = clf.classify(token) # pos(parts of speech), 순서대로 T_adjective, T_adverb, T_verb, T_nouns

    
    # mongoDB 에 입력
    collectionname = update_db()   # 전처리하고자하는 collection명을 인스턴스로 바꿀 것
    collectionname.setdbinfo()     # collection명.setdbinfo()  
    collectionname.insertone(gd, cno ,title, ccontent, idate, token, pos)     # collection명.insertone() 
    
    # json 파일 생성
    #collectionname.make_json('token_ruri.json',gd, title, ccontent, idate, clinks, creplies, token, pos)

    lasttime = time.time()
    mem_after = process.memory_info().rss / 1024 / 1024
    timehisory.append(lasttime-startime)
    memory.append(mem_after)

    print(i,'번째 루프 도는 중','소요시간', lasttime-startime)
    print('시작 전 메모리 사용량: {} MB'.format(mem_before))
    print('종료 후 메모리 사용량: {} MB'.format(mem_after))
    print('루프 한번 도는데 걸린 시간',timehisory)
    print('루프 한번 도는데 쓰인 메모리',memory)

