# preprocessing

-전처리 프로그램 사용 방법

1. config.1.ini 파일에서 콜랙션 이름 설정할 것
   
   ex) collection = womad  


2. cleaner.py 에서 전처리 하고자 하는 콜랙션 이름 넣을 것
   
   ex) collectionname =  'womad' 

3. 전처리할 범위 지정
     10000 개의 다규먼트를 전처리하고자 할 떄
    ex) for i in range(0,10):
        startime = time.time()
        
        total = 1000 # 1번 반복문 돌릴 때 1000의 다큐멘트 가져오기
