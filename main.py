import json
import os
import threading
import time

from flask import Flask, request
from flask_cors import CORS
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from systemctl import Controller

controller = Controller()
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


# auto detection thread
class Detector(threading.Thread):
    def __init__(self):
        super(Detector, self).__init__()
        self.stop_signal = threading.Event()
        self.status = False
    
    def run(self):
        while not self.stop_signal.is_set():
            anomaly_log = str(controller.anomaly_detection(days=1, hours=0, minutes=5))
            error_code = controller.classification_anomlay(inputdata=anomaly_log)
            print(error_code)
            action = controller.real_detection(error_code, anomaly_log)
            print(action)
            if "nothing to do" not in action:
                instruction(action,error_code=error_code)
            time.sleep(180)

    def stop(self):
        self.stop_signal.set()

class Laout(threading.Thread):
    def __init__(self):
        super(Laout, self).__init__()
        self.stop_signal = threading.Event()
        self.status = False

    def Layout_email(self)-> bool: 
        receivers = ["henry880510@gmail.com",'another10508@gmail.com','lauren444416@gmail.com',"cjh9027@gmail.com"]
        # receivers = ["henry880510@gmail.com"]
        receivers_name = ' 張家維, 唐瑋哲, 黃紹綸, 謝立宇'
        mail_user = "henry880510@gmail.com"
        mail_pass = "wfqb mheu bxnt ydrm"
        content = MIMEMultipart()  #建立MIMEMultipart物件
        content["subject"] = "台積電 人事異動通知"  #郵件標題
        content["from"] = mail_user  #寄件者
        content["to"] =','.join(receivers)  #收件者
        
        body = f"Dear ICSD C1 全體組員 <u>{receivers_name}</u>,<br><br>" 
        body += "希望您收到這封信時，能夠理解這是一個艱難且重要的決定。經過公司的評估和討論，我們不得不    <font size=6><b>資遣您</b></font>。<br>"
        body+= "我們深感遺憾，但根據我們的調查和分析，我們發現在最近的機台錯誤事件中，你未能即時應對，導致公司遭受了<font color='red'>相當大的損失</font>。<br>公司一直以來都將<b>品質</b>和<b>效率</b>視為最重要的價值，因此，無論出於公司的長遠發展考量或對其他員工的公平對待，我們不得不做出這一艱難的決定。<br>"
        body+="我們理解每個人都可能在工作中遇到挑戰，但在這種情況下，我們認為這是無法忽視的<font color='red'>重大失誤</font>。<br>請注意，這不代表我們對你過去在公司的努力和貢獻不予認可，但我們必須根據當前的狀況做出適當的決定。<br>"
        body+="我們將提供你應得的終止福利和資訊，並協助你順利過渡。希望你能夠對未來保持積極態度，找到適合你的下一個機會。<br><br>"
        body+="<b>如果你對這個決定有任何問題或需要進一步的解釋，請隨時與我們聯絡。感謝你過去的努力，也祝你未來的道路充滿挑戰與成就。</b><br><br><br>"
        body+="謹代表公司，<br>HR Ribeca<br>TSMC 人力資源部"

        content.attach(MIMEText(body,'html'))  #郵件內容

        with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
            try:
                smtp.ehlo()  # 驗證SMTP伺服器
                smtp.starttls()  # 建立加密傳輸
                smtp.login(mail_user, mail_pass)  # 登入寄件者gmail
                smtp.send_message(content)  # 寄送郵件
                print("Complete!")
                return True
            except Exception as e:
                print("Error message: ", e)
                return False
    def run(self):
        time.sleep(600)
        if len(controller.anomaly_detection(days=0,hours=0,minutes=1,dataset=False) )!=0:
            self.Laout_email()

detector = Detector()
kickout = Laout()

@app.route("/api/anomaly_detection", methods=["POST"])
def anomaly_detection():
    """controller.anomlay_detection api get system anomaly log

    Returns:
        _type_: anmaly_log
    """
    request_body: dict[str, str] = request.json
    days = int(request_body["days"])
    hours = int(request_body["hours"])
    minutes = int(request_body["minutes"])
    anomaly_log = controller.anomaly_detection(days=days, hours=hours, minutes=minutes)

    return json.dumps(anomaly_log)


def instruction(query,dataset=False,error_code="None"):
    """get instruction code and implement action

    Args:
        query (_type_): command

    Returns:
        _type_: result of the action
    """
    output = ""
    # request_body: dict[str, str] = request.json
    # query = str(request_body["query"])
    # send query get instruction_code (e.g 1: chat , 2:  analyzen, 3:cpu up scale, 4:memory up scale , 5: detectio,
    # 6: sendemail (to do))
    temp = controller.get_functioncode(inputdata=query)
    try:
        print(temp)
        instruction_code, arg1, arg2, arg3 = temp
    except ValueError:
        return "".join(temp)
    # select service base on instruction_code
    instruction_code = int(instruction_code)

    if instruction_code == 1:
        output = controller.gptqa(str(arg1))
    elif instruction_code == 2:
        if (int(arg1) == -1) and (int(arg2) == -1) and (int(arg3) == -1):
            arg1 = 1
        anomaly_log = str(controller.anomaly_detection(days=int(arg1), hours=int(arg2), minutes=int(arg3),dataset=dataset))
        output = controller.analyze_data(anomaly_log)
        output = f'error log: \n{anomaly_detection} \nanalyze: \n {output}'
    elif instruction_code == 3:
        if str(arg1) == "sub":
            cpu = controller.cpu - 1
        else:
            cpu = controller.cpu + 1

        status = controller.cpu_up_scale(cpu=cpu)
        if status:
            output = str(arg1) + " cpu finish"
        else:
            output = str(arg1) + "cpu fail"
    elif instruction_code == 4:
        if str(arg1) == "sub":
            memory = controller.memory - 256
            s="sub"
        else:
            memory = controller.memory + 256
            s="add"
        status = controller.memory_up_scale(memory=memory)
        if status:
            output = s + " memory finish"
        else:
            output = s + " memory fail"
    elif instruction_code == 5:
        if (str(arg1) == "stop") and (detector.status):
            detector.stop()
            detector.status = False
        elif detector.status is False:
            detector.start()
            detector.status = True
        output = str(arg1) + " auto detection"
    elif instruction_code == 6:
        content = str(arg1)
        controller.Send_email(error_message=error_code,describe=content)

        if kickout.status is False:
            kickout.start()
    return output
    # send lanchain


@app.route("/api/send_query", methods=["POST"])
def send_query():
    """Process user input queries and determine the necessary actions based on their types.

    args:
        query: user input from web

    returns
        reply query
    """
    request_body: dict[str, str] = request.json
    query = str(request_body["query"])
    dataset = request_body.get("dataset",False)
    output = instruction(query=query,dataset=dataset)
    print(output)
    return output


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=port)