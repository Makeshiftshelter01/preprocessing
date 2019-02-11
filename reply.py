import os.path, re
import pandas as pd

# def cleaning(fname):
#     with open(fname, 'r', encoding='utf-8') as f: text = f.readlines()
#     lines = []
#     for i in range(len(text)):
#         lines.append(text[i])
#     print(lines[1:5])

# cleaning('e:/teamproject/naver/po06.csv')

pd.set_option('display.max_columns', None)  
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', -1)
text = []
def cleaning(fname):
    rawdata = pd.read_csv(fname)
    #for i in range(len(rawdata['댓글'])):
    #print(rawdata.head())
    for i in range(200,250):
        data = re.sub(r'\\\n\r\s\d\w','',str(rawdata['댓글'][i])) 
        data = re.sub(r'\d+[가-힣]',' ',data)
        data = re.sub(r'\\*' ,'', data) 
        data = re.sub(r'[A-Za-z0-9\(\)]*','',data) 
        data = re.sub(r'[&gt;]*','',data) 
        data = re.sub(r'[\?\%\!\#\.\,\"\-\&\~\^\/]',' ',data)
        data = re.sub(r'$',' ',data)
        data = re.sub('[^\x00-\x7F\uAC00-\uD7AF]',' ',data)
        text.append(data)  
    return text


a = cleaning('e:/teamproject/naver/po06.csv')
print(a)
