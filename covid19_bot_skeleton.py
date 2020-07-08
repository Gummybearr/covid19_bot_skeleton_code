from bs4 import BeautifulSoup
import requests
import telegram

#대구
request = requests.get('http://www.daegu.go.kr/')
html = request.text
soup = BeautifulSoup(html, "html.parser")
covid19div = soup.findAll('div', {'class': 'wrap_con'})
covid19data = soup.findAll('div', {'class': 'count'})

dgupdate = 1
dgdb = [] #총계, 격리해제, 격리중, 사망
for covdata in covid19data:
    dgupdate = covdata.findAll('p')
    for i in dgupdate:
        dgupdate = i.text
    cnt = covdata.findAll('li')
    for i in cnt:
        dgdb.append(i.text)

dgmessage = "<대구지역 환자 발생 현황> \n"+"총계: "+dgdb[0][5:]+"\n격리: "+dgdb[2][9:]+"\n해제: "+dgdb[1][9:]+"\n사망: "+dgdb[3][3:]+"\n업데이트: "+dgupdate[:-2]+"\n출처: http://www.daegu.go.kr/"
print(dgmessage)

#전국
request = requests.get("https://search.naver.com/search.naver?sm=top_hty&fbm=1&ie=utf8&query=%EC%BD%94%EB%A1%9C%EB%82%9819")
html = request.text
soup = BeautifulSoup(html, "html.parser")
dbdata = soup.findAll('strong', {"class": "num"})
updates = soup.findAll('div', {"class": "csp_notice_info"})

# 확진환자, 격리해제, 검사진행, 사망자
alldb = []
for i in dbdata:
    alldb.append(i.text)
    
alldb2int = int(alldb[0][:-4])*1000+int(alldb[0][-3:])-int(alldb[1])
alldb[2] = str(int(alldb2int/1000))+","+str(alldb2int%1000)

for i in updates:
    allupcap = i.text    
allupdate = allupcap[46:63]
allmessage = "<전국 환자 발생 현황> \n"+"확진: "+alldb[0]+"\n격리: "+alldb[2]+"\n해제: "+alldb[1]+"\n사망: "+alldb[3]+"\n업데이트: "+allupdate+"\n출처: https://www.naver.com"
print(allmessage)

#경기
request = requests.get("https://www.gg.go.kr/bbs/boardView.do?bsIdx=464&bIdx=2296956&menuId=1535")
html = request.text
soup = BeautifulSoup(html, "html.parser")
dbdata = soup.findAll('div', {"class": "corona_confirmation"})
updates = soup.findAll('div', {"class": "corona_top_title"})

ggdb=[] 
ggupdate=0
    
for data in dbdata:
    datas = data.findAll('td')
    for data in datas:
        ggdb.append(data.text)

ggupdate = updates[0].text

#확진 격리 환자, 격리 해제, 사망, 확진 환자
ggmessage = "<경기지역 환자 발생 현황> \n"+"확진: "+ggdb[0]+"\n격리: "+ggdb[1]+"\n해제: "+ggdb[2]+"\n사망: "+ggdb[2]+"\n업데이트: 20"+ggupdate[2:-4]+"\n출처: https://www.gg.go.kr"
print(ggmessage)

#메시지 보내기
bot = telegram.Bot(token='____________')
receivers=[]
try:
    with open('subsiddb.txt', 'r+') as f:
        for line in f:
            receivers.append(line)
except:
    f = open("subsiddb.txt", 'a+')
    for i in bot.getUpdates():
        receivers.append(str(i['message']['chat']['id']))
    receivers = list(set(receivers))
    
    for i in range(0, len(receivers)):
        if i==len(receivers)-1:
            f.writelines(str(receivers[i]))
        else:
            f.writelines(str(receivers[i])+"\n")
    f.close()

for i in range(0, len(receivers)):
    if receivers[i][-1]=="\n":
        receivers[i] = receivers[i][:-1]

receivers = list(set(receivers))
print(receivers)

try:
    f = open("test.txt", 'r')
    f.close()
except:
    f = open("test.txt", 'w')
    f.write(allupdate+"\n")
    f.write(ggupdate+"\n")
    f.write(dgupdate)
    f.close()

#all gg db 
updateflag = [0,0,0]

reads = [allupdate, ggupdate, dgupdate]
print(reads)

i = 0
with open('test.txt', 'r+') as f:
    for line in f:
        print(line)
        if(line.startswith(reads[i])):
            updateflag[i]=0
            print("identical")
        else:
            lines = reads[i]
            updateflag[i]=1
            print("not identical")
        i+=1
    

i = 0  
print(updateflag)

with open('test.txt', 'w') as f:
    for read in reads:
        print(read)
        if updateflag[i]==1:
            if i<2:
                f.writelines(read+"\n")
            else:
                f.writelines(read)
            print('updating line',i)
        else:
            if i<2:
                f.writelines(read+"\n")
            else:
                f.writelines(reads[i])
        i+=1

for i in receivers:
    try:
        print(i)
        if updateflag[0]==0 and updateflag[1]==0 and updateflag[2]==0:
            bot.send_message(chat_id=i, text="질병관리본부에 업데이트된 자료가 없습니다")
            if i=="__________":
                bot.send_message(chat_id=i, text="_________")
            continue
        if updateflag[0]==1:
            bot.send_message(chat_id=i, text=allmessage)
        if i=="___________":
            if updateflag[1]==1:
                bot.send_message(chat_id=i, text=ggmessage)
            if updateflag[2]==1:
                bot.send_message(chat_id=i, text=dgmessage)
        elif i=="__________":
            if updateflag[0]==0 and updateflag[1]==0:
                bot.send_message(chat_id=i, text="업데이트 된 자료가 없대... 업데이트되면 다시 보내줄게:)")
                continue
            if updateflag[1]==1:
                bot.send_message(chat_id=i, text=ggmessage)
            bot.send_message(chat_id=i, text="_______________")
        else:
            if updateflag[2]==1:
                bot.send_message(chat_id=i, text=dgmessage)
            bot.send_message(chat_id=i, text="오늘도 안전한 하루 보내세요!")
    except:
        print("something wrong")
