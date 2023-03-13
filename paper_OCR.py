import easyocr
import numpy as np
import re


from PIL import ImageFont, ImageDraw, Image

class ocr_Reader:
    def __init__(self, imgpath = ""):
        self.path = imgpath # 이미지 경로
        
        file = open("bank_list_KOR.txt", 'r', encoding="utf8") # 한국 은행 리스트
        
        bank_list = file.readlines()
        tmp = []
        for txt in bank_list:
            tmp.append(txt.replace("\n", ''))
        self.bank_list = tmp
        file.close()

        file = open("address_list_KOR.txt", 'r', encoding="utf8") # 한국 주소 리스트(길까지)
        addr_list = file.readlines()
        tmp = []
        for txt in addr_list:
            tmp.append(txt.replace("\n", ''))
        self.addr_list = tmp
        file.close()

        file = open("cards_list_KOR.txt", 'r', encoding="utf8") # 한국 카드사 리스트
        card_list = file.readlines()
        tmp = []
        for txt in card_list:
            tmp.append(txt.replace("\n", ''))
        self.card_list = tmp
        file.close()
        
        # OCR Reader 설정
        self.reader = easyocr.Reader(['ko', 'en'], gpu = True) 

    #유사도 검사
    def get_Jaccard_sim(self, tokens1, tokens2): #Jaccard 유사도 추출
        
        doc_union = set(tokens1).union(set(tokens2))
        doc_intersection = set(tokens1).intersection(set(tokens2))
        jaccard_similarity = len(doc_intersection) / len(doc_union)
        
        return float(jaccard_similarity)
    
    #텍스트 후처리
    def post_processing(self, key = "", txt = ""):
        #키워드 별 후처리
        if key == "contractor" or key == "depositor" or key == "cardholder" : 
            #불용어 제거
            txt = txt.replace("(", "").replace(")", "")
            txt = txt.replace(" ", "")
            return ["성공", txt]
        
        elif key == "PID" : 
            #불용어 제거
            txt = txt.replace(" ","")
            txt = txt.replace("6자리","")
            
            #숫자만 걸러내기
            txt = re.sub(r"[^0-9]", "", txt)
            if len(txt) != 6:
                return ["수정필요", txt]
            else : 
                return ["성공", txt]
        
        elif key == "office_Addr" or key == "home_Addr":
            txt = txt.replace('',' ')
            txt = txt.split(" ")
            result_tmp = list(filter(None, txt))

            sim = 0

            for word in self.addr_list:
                word_splited = word.replace('',' ')
                word_splited = word_splited.split(" ")
                word_splited = list(filter(None, word_splited))
                
                sim_now = self.get_Jaccard_sim(result_tmp, word_splited)
                
                #리스트 가운데 가장 유사도가 높은 길 주소로 교정
                if sim_now > sim:
                    sim = sim_now
                    txt = word
                    
                else:
                    pass
            return ["성공", txt]
        
        elif key == "bankName":
            txt = txt.replace("(", "").replace(")", "")
            txt = txt.replace('',' ')
            txt = txt.split(" ")

            result_tmp = list(filter(None, txt))
            sim = 0
            #리스트 가운데 가장 유사도가 높은 은행이름으로 교정
            for word in self.bank_list:
                word_splited = word.replace('',' ')
                word_splited = word_splited.split(" ")
                word_splited = list(filter(None, word_splited))
                
                sim_now = self.get_Jaccard_sim(result_tmp, word_splited)
                if sim_now > sim:
                    sim = sim_now
                    txt = word
                    
                else:
                    pass
            return ["교정됨", txt]
        
        elif key == "cardName":
            txt = txt.replace("(", "").replace(")", "")
            txt = txt.replace('',' ')
            
            txt = txt.split(" ")

            result_tmp = list(filter(None, txt))
            
            sim = 0
            #리스트 가운데 가장 유사도가 높은 카드이름으로 교정
            for word in self.card_list:
                word_splited = word.replace('',' ')
                word_splited = word_splited.split(" ")
                word_splited = list(filter(None, word_splited))
                sim_now = self.get_Jaccard_sim(result_tmp, word_splited)
                if sim_now > sim:
                    sim = sim_now
                    txt = word
                    
                else:
                    pass
            return ["교정됨", txt]
        
        elif key == "acc_bank":
            txt = re.sub(r"[^0-9]", "", txt)
            return ["성공", txt]

        elif key == "cardNum":
            txt = re.sub(r"[^0-9]", "", txt)
            txt = txt[:4] + "-" + txt[4:8] + "-"+ txt[8:]
            return ["성공", txt]
        
        elif key == "expiration":
            txt = re.sub(r"[^0-9]", "", txt)
            txt = txt[:2] + "/" + txt[2:]
            return ["성공", txt]
        
        elif key == "num_acc":
            txt = re.sub(r"[^0-9]", "", txt)
            return ["성공", txt]
        elif key == "date":
            year =  txt[:txt.find("년")]
            year = re.sub(r"[^0-9]", "", year)
            if year == "":
                year = "재입력 필요"
            month =  txt[txt.find("년"):txt.find("월")]
            month = re.sub(r"[^0-9]", "", month)
            if month == "":
                month = "재입력 필요"
            day = txt[txt.find("월"):txt.find("일")]
            day = re.sub(r"[^0-9]", "", day)
            if day == "":
                day = "재입력 필요"
            txt = {"year" : year, "month" : month, "day" : day}
            
            return ["성공", txt]


    def get_Data(self, key =""):
        if key == "contractor": # 계약자 성명
            x1 = 310
            y1 = 23
            x2 = 736
            y2 = 78
        
        elif key == "PID" : #주민등록번호
            x1 = 731
            y1 = 10
            x2 = 1310
            y2 = 70
        
        elif key == "office_Addr": # 직장주소
            x1 = 310
            y1 = 82
            x2 = 1384
            y2 = 130

        elif key == "home_Addr": # 자택주소
            x1 = 313
            y1 = 205
            x2 = 1393
            y2 = 255
        
        elif key == "depositor": # 예금주
            x1 = 393
            y1 = 266
            x2 = 812
            y2 = 317

        elif key == "cardholder": #카드주
            x1 = 393
            y1 = 330
            x2 = 812
            y2 = 375
        
        elif key == "bankName": #은행명
            x1 = 809
            y1 = 256
            x2 = 974
            y2 = 311

        elif key == "cardName": #카드명
            x1 = 809
            y1 = 315
            x2 = 974
            y2 = 373
        
        elif key == "acc_bank": #계좌번호
            x1 = 970
            y1 = 250
            x2 = 1400
            y2 = 300
        
        elif key == "cardNum": #카드번호
            x1 = 970
            y1 = 310
            x2 = 1190
            y2 = 367

        elif key == "expiration": #유효일자
            x1 = 1187
            y1 = 305
            x2 = 1400
            y2 = 360
        
        elif key == "num_acc": #구좌
            x1 = 312
            y1 = 388
            x2 = 812
            y2 = 435
        
        elif key == "date": #계약일자
            x1 = 390
            y1 = 670
            x2 = 700
            y2 = 720

        image = Image.open(self.path)
        image = image.crop((x1, y1, x2, y2))     
        image.show()
        image.save("tmp.jpg")
        image.close()

        #OCR Reading
        result = self.reader.readtext('tmp.jpg')
        
        result_ = []
        for i in result:
            result_.append(str(i[1]))
          
        result_ = "".join(result_)
        
        #후처리
        result = self.post_processing(txt = result_, key=key)

        return {"key" : key,"msg" : result[0], "txt" : result[1]}

        

        
       


        