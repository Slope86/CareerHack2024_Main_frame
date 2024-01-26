import json
import os
from io import StringIO

import pandas as pd
import requests
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

load_dotenv()

USERNAME = os.getenv("API_ADMIN_USERNAME")
PASSWORD = os.getenv("API_ADMIN_PASSWORD")
LLMAPI = os.getenv("LLM_API")
APIURL = os.getenv("API_URL")


class Controller:
    def __init__(
        self,
        system_metric_url: str = APIURL + "/api/system_metric",
        up_scale_url: str = APIURL + "/api/cloud_run_upscale",
        get_functioncode_url: str = LLMAPI + "/api/get_functioncode",
        login_url: str = APIURL + "/api/login",
        classification_anomlay_url: str = LLMAPI + "/api/class_anomaly",
        analyze_data_url: str = LLMAPI + "/api/analyze_data",
        gptqa_url: str = LLMAPI + "/api/gptqa",
        real_detection_url: str = LLMAPI + "/api/real_detection",
        sorter_log_url:str = LLMAPI + "/api/sort_log",
        username: str = USERNAME,
        password: str = PASSWORD,
        cpu: int = 1,
        memory: int = 512,
    ):
        """initialization

        Args:
            system_metric_url (str, optional): url of system metric api. Defaults to APIURL+"/api/system_metric".
            up_scale_url (str, optional): url of up scale api. Defaults to APIURL+"/api/cloud_run_upscale".
            login_url (str, optional): url of login api. Defaults to APIURL+"/api/login".
            username (str, optional): login username. Defaults to USERNAME.
            password (str, optional): login passward. Defaults to PASSWORD.
            cpu (int, optional): used cpu. Defaults to 1.
            memory (int, optional): used memory. Defaults to 512.

        """
        self.anomaly_log = {}
        self.__system_metric_url = system_metric_url
        self.__up_scale_url = up_scale_url
        self.__get_functioncode_url = get_functioncode_url
        self.__classification_anomlay_url = classification_anomlay_url
        self.__analyze_data_url = analyze_data_url
        self.__gptqa_url = gptqa_url
        self.__login_url = login_url
        self.__real_detection_url = real_detection_url
        self.__sorter_log_url = sorter_log_url
        self.__username = username
        self.__password = password
        self.receivers = ["henry880510@gmail.com",'another10508@gmail.com','lauren444416@gmail.com',"cjh9027@gmail.com"]

        self.cpu = cpu
        self.memory = memory

        self.cpu_up_scale(cpu=cpu)
        self.memory_up_scale(memory=memory)

    def login_api(self) -> json:
        """use user passward  get permission to use api

        Returns:
            json: access_token to use api
        """
        data = {"username": self.__username, "password": self.__password}
        response = requests.post(self.__login_url, json=data)
        return response.json().get("access_token")
    
    def Send_email(self,error_message:str=None,describe:str=None): 
        receivers = ["henry880510@gmail.com",'another10508@gmail.com','lauren444416@gmail.com',"cjh9027@gmail.com"]

        mail_user = "henry880510@gmail.com"
        mail_pass = "wfqb mheu bxnt ydrm"
        content = MIMEMultipart()  #建立MIMEMultipart物件
        content["subject"] = "VM:dvwa Error Alert"  #郵件標題
        content["from"] = mail_user  #寄件者
        content["to"] =','.join(receivers)  #收件者
        
        body = f"Dear <u>Colleague</u>,<br><br>" 
        body += f"error log: <font color='red'><b>{error_message}</b></font> in the ongoing plan.<br>"
        body += "describe: <br>"
        body += describe.replace("\n","<br>")+"<br>"
        body += "Please address it as soon as possible.<br>" 
        body +="VM:dvwa     Region: us-central1     URL：<a href='https://gcp-asst-bot-3ygjg5oe3q-uc.a.run.app/'>https://gcp-asst-bot-3ygjg5oe3q-uc.a.run.app/</a>"
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

    def real_detection(self, inputdata: str = None, ori_log: str = None) -> str:
        """real time detection input error dict from classification anomaly api

        Args:
            inputdata (str, optional): error dict to str.

        Returns:
            str: system action base on error dict
        """
        access_token = self.login_api()
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {"inputdata": inputdata, "ori_log": ori_log}
        response = requests.post(self.__real_detection_url, json=data, headers=headers)
        response_json = response.json()

        return response_json

    def get_functioncode(self, inputdata: str = None) -> list:
        """get instruction code from genAI

        Args:
            inputdata (str, optional): query

        Returns:
            list: ['instruction code','arg','arg','arg']
        """
        access_token = self.login_api()
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {"inputdata": inputdata}
        response = requests.post(self.__get_functioncode_url, json=data, headers=headers)
        response_json = response.json()
        
        return response_json

    def classification_anomlay(self, inputdata: str = None) -> dict:
        """generator error dict from anomaly log

        Args:
            inputdata (str, optional): anomaly log(dict) to str.

        Returns:
            dict: error dict
        """
        access_token = self.login_api()
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {"inputdata": inputdata}
        response = requests.post(self.__classification_anomlay_url, json=data, headers=headers)
        response_json = response.json()

        return response_json

    def analyze_data(self, inputdata: str = None) -> str:
        """summarize histories system data

        Args:
            inputdata (str, optional): anomaly log(dict) to str

        Returns:
            str: analyze for histories data
        """
        access_token = self.login_api()
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {"inputdata": inputdata}
        response = requests.post(self.__analyze_data_url, json=data, headers=headers)
        print(response)
        response_json = response.json()
        return response_json

    def sort_log(self,inpudata:str=None)->str:
        
        access_token = self.login_api()
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {"inputdata": inpudata}
        response = requests.post(self.__sorter_log_url, json=data, headers=headers)
        response_json = response.json()
        return response_json
    
    def gptqa(self, query: str = None) -> str:
        """general gpt qa

        Args:
            query (str, optional): query.

        Returns:
            str: reply
        """
        access_token = self.login_api()
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {"query": query}
        response = requests.post(self.__gptqa_url, json=data, headers=headers)
        response_json = response.json()

        return response_json

    def get_system_metric(self, metric: str, days: int = 0, hours: int = 0, minutes: int = 0) -> pd.DataFrame:
        """call api get system_metric. the request type must be POST, not GET.


        Args:
            metric (str): metric tpye must be one of the [
            "request_count",
            "request_latencies",
            "instance_count",
            "CPU_utilization",
            "memory_utilization",
            "startup_latency"
            ]
            days (int, optional): data from n days ago. Defaults to 0.
            hours (int, optional): data from n hour ago. Defaults to 0.
            minutes (int, optional): data from n minute ago. Defaults to 0.

        Returns:
            pd.DataFrame: Specified Conditions DataFrame
        """
        access_token = self.login_api()
        headers = {"Authorization": f"Bearer {access_token}"}

        # Metrics:
        # "request_count",
        # "request_latencies",
        # "instance_count",
        # "CPU_utilization",
        # "memory_utilization",
        # "startup_latency"
        data = {"metric": metric, "days": days, "hours": hours, "minutes": minutes}
        # get request to the API
        response = requests.post(self.__system_metric_url, json=data, headers=headers)
        response_json = response.json()

        df = pd.read_json(StringIO(response_json))

        return df

    def cpu_up_scale(self, cpu: int = 1) -> bool:
        """adjust cloud cpu limit, 1 cpu = 1000m

        Args:
            cpu (int, optional): how many cpu  will be utilized. Defaults to 1.

        Returns:
            bool: whether request was successful
        """
        access_token = self.login_api()
        headers = {"Authorization": f"Bearer {access_token}"}

        cpu_limit = str(cpu * 1000) + "m"

        data = {
            "cpu_limit": cpu_limit,
        }

        # get request to the API
        response = requests.post(self.__up_scale_url, json=data, headers=headers)

        if response.status_code == 200:
            self.cpu = cpu
            return True
        return False

    def memory_up_scale(self, memory: int = 512) -> bool:
        """adjust cloud memory limit (Mi).

        Args:
            memory (int, optional): How much memory in Mi (Mebibytes) will be utilized. Defaults to 512.

        Returns:
            bool: whether request was successful
        """
        access_token = self.login_api()
        headers = {"Authorization": f"Bearer {access_token}"}

        memory_limit = str(memory) + "Mi"

        data = {"memory_limit": memory_limit}

        # get request to the API
        response = requests.post(self.__up_scale_url, json=data, headers=headers)

        if response.status_code == 200:
            self.memory = memory
            return True
        return False

    def cpu_limit_detection(self, threshold: int = 60, data: pd.DataFrame = None, col_class: dict = None) -> None:
        """detection cpu limit whether >= threshold

        Args:
            threshold (int, optional): cpu limit threshold. Defaults to 60.
            data (pd.DataFrame, optional): system data whether from dataset or real time system. Defaults to None.
            col_class (dict, optional): columns name for all feature. Defaults to None.
        """
        time_minute = 0
        for index, row in data.loc[:, col_class["cpu"]].iterrows():
            for _, value in row.items():
                if int(value) >= threshold:
                    time_minute += 1
                else:
                    time_minute = 0

                if time_minute >= 2:
                    if index not in self.anomaly_log:
                        request_count = " ".join(
                            [
                                " ".join([f"{col}={val} times." for col, val in row.items()])
                                for index, row in data.loc[[index], col_class["request_count"]].iterrows()
                            ]
                        )
                        self.anomaly_log[
                            str(index)
                        ] = f"CPU utilization {value}% (>=60%). \
                        other information: cpu:{data.loc[index,col_class['cpu']].values[0]}% \
                        memory:{data.loc[index,col_class['memory']].values[0]}% \
                        instance_count:{data.loc[index,col_class['instance']].values[0]} \
                        request_count:{request_count} \
                        request_latencies:{data.loc[index,col_class['request_latencies']].values[0]} ms".replace(
                            "  ", ""
                        )
                    else:
                        self.anomaly_log[str(index)] = (
                            f",CPU utilization {value}% (>=60%)," + self.anomaly_log[str(index)]
                        )

    def memory_limit_detection(self, threshold: int = 60, data: pd.DataFrame = None, col_class: dict = None) -> None:
        """detection memort limit whether >= threshold

        Args:
            threshold (int, optional): memory limit threshold. Defaults to 60.
            data (pd.DataFrame, optional): system data whether from dataset or real time system. Defaults to None.
            col_class (dict, optional): columns name for all feature. Defaults to None. Defaults to None.
        """
        time_minute = 0
        for index, row in data.loc[:, col_class["memory"]].iterrows():
            for _, value in row.items():
                if int(value) >= threshold:
                    time_minute += 1
                else:
                    time_minute = 0

                if time_minute >= 2:
                    if index not in self.anomaly_log:
                        request_count = " ".join(
                            [
                                " ".join([f"{col}={val} times." for col, val in row.items()])
                                for index, row in data.loc[[index], col_class["request_count"]].iterrows()
                            ]
                        )
                        self.anomaly_log[
                            str(index)
                        ] = f"memory utilization {value}% (>=60%). \
                        other information: cpu:{data.loc[index,col_class['cpu']].values[0]}% \
                        memory:{data.loc[index,col_class['memory']].values[0]}% \
                        instance_count:{data.loc[index,col_class['instance']].values[0]} \
                        request_count:{request_count} \
                        request_latencies:{data.loc[index,col_class['request_latencies']].values[0]} ms".replace(
                            "  ", ""
                        )
                    else:
                        self.anomaly_log[str(index)] = (
                            f",memory  utilization {value}% (>=60%)" + self.anomaly_log[str(index)]
                        )

    def cloud_run_restart_detection(self, data: pd.DataFrame = None, col_class: dict = None) -> None:
        """detection system restart

        Args:
            data (pd.DataFrame, optional):  system data whether from dataset or real time system. Defaults to None.
            col_class (dict, optional): columns name for all feature. Defaults to None. Defaults to None.
        """
        for index, row in data.loc[:, col_class["start"]].iterrows():
            for _, value in row.items():
                if int(value) != 0:
                    if index not in self.anomaly_log:
                        request_count = " ".join(
                            [
                                " ".join([f"{col}={val} times." for col, val in row.items()])
                                for index, row in data.loc[[index], col_class["request_count"]].iterrows()
                            ]
                        )
                        self.anomaly_log[
                            str(index)
                        ] = f"cloud run restart at {value} ms. \
                        other information: cpu:{data.loc[index,col_class['cpu']].values[0]}% \
                        memory:{data.loc[index,col_class['memory']].values[0]}% \
                        instance_count:{data.loc[index,col_class['instance']].values[0]} \
                        request_count:{request_count} \
                        request_latencies:{data.loc[index,col_class['request_latencies']].values[0]} ms".replace(
                            "  ", ""
                        )
                    else:
                        self.anomaly_log[str(index)] = (
                            f",cloud run restart at {value} ms" + self.anomaly_log[str(index)]
                        )

    def instance_count_detection(self, data: pd.DataFrame = None, col_class: dict = None) -> None:
        """detection instance whether >= 2

        Args:
            data (pd.DataFrame, optional):  system data whether from dataset or real time system. Defaults to None.
            col_class (dict, optional): columns name for all feature. Defaults to None. Defaults to None.
        """
        for index, row in data.loc[:, ["Instance Count (active)"]].iterrows():
            for _, value in row.items():
                if int(value) >= 2:
                    if index not in self.anomaly_log:
                        request_count = " ".join(
                            [
                                " ".join([f"{col}={val} times." for col, val in row.items()])
                                for index, row in data.loc[[index], col_class["request_count"]].iterrows()
                            ]
                        )
                        self.anomaly_log[
                            str(index)
                        ] = f"instance count={value} (>= 2). \
                        other information: cpu:{data.loc[index,col_class['cpu']].values[0]}% \
                        memory:{data.loc[index,col_class['memory']].values[0]}% \
                        instance_count:{data.loc[index,col_class['instance']].values[0]} \
                        request_count:{request_count} \
                        request_latencies:{data.loc[index,col_class['request_latencies']].values[0]} ms".replace(
                            "  ", ""
                        )
                    else:
                        self.anomaly_log[str(index)] = f",instance count={value} (>= 2)" + self.anomaly_log[str(index)]

    def request_fail(self, data: pd.DataFrame = None, col_class: dict = None) -> None:
        """detection request fail error

        Args:
            data (pd.DataFrame, optional): system data whether from dataset or real time system. Defaults to None.
            col_class (dict, optional): columns name for all feature. Defaults to None.. Defaults to None.
        """
        for index, row in data.loc[:, col_class["request_count"]].iterrows():
            for columnname, value in row.items():
                status_code = str(columnname)
                if ((status_code[0] == "5") or (status_code[0] == "4")) and (int(value) > 0):
                    if index not in self.anomaly_log:
                        request_count = " ".join(
                            [
                                " ".join([f"{col}={val} times." for col, val in row.items()])
                                for index, row in data.loc[[index], col_class["request_count"]].iterrows()
                            ]
                        )
                        self.anomaly_log[
                            str(index)
                        ] = f"request fail. error code: {status_code}. \
                        other information: cpu:{data.loc[index,col_class['cpu']].values[0]}% \
                        memory:{data.loc[index,col_class['memory']].values[0]}% \
                        instance_count:{data.loc[index,col_class['instance']].values[0]} \
                        request_count:{request_count} \
                        request_latencies:{data.loc[index,col_class['request_latencies']].values[0]} ms".replace(
                            "  ", ""
                        )

                    else:
                        self.anomaly_log[str(index)] = (
                            f"request fail. error code: {status_code}." + self.anomaly_log[str(index)]
                        )

    def anomaly_detection(
        self, days: int = 0, hours: int = 5, minutes: int = 0, datasetpath: str = "./dataset/", dataset: bool = False
    ) -> dict:
        """anomaly threshold:
            CPU utilization >= 60% 2mins
            Memory utilization >= 60% 2mins
            Cloud run re-start (startup_latency != 0)
            Instance count >= 2
            Fail Response (requset count 4xx,5xx)

        Args:
            days (int, optional): n days ago data from real time system. Defaults to 0.
            hours (int, optional): n hours ago data from real time system. Defaults to 5.
            minutes (int, optional): n minutes ago data from real time system. Defaults to 0.
            datasetpath (str, optional): datasetpath. Defaults to "./".
            dataset (bool, optional): whether use data set. Defaults to False.

        Returns:
            dict: anomaly log
        """

        if dataset is False:
            instance = self.get_system_metric(metric="instance_count", days=days, hours=hours, minutes=minutes)
            cpu = self.get_system_metric(metric="CPU_utilization", days=days, hours=hours, minutes=minutes)
            memory = self.get_system_metric(metric="memory_utilization", days=days, hours=hours, minutes=minutes)
            startup_latency = self.get_system_metric(metric="startup_latency", days=days, hours=hours, minutes=minutes)
            requests_count = self.get_system_metric(metric="request_count", days=days, hours=hours, minutes=minutes)
            requests_latencies = self.get_system_metric(
                metric="request_latencies", days=days, hours=hours, minutes=minutes
            )
            instance.columns = ["Instance Count (active)", "Instance Count (idle)"]
            cpu.columns = ["Container CPU Utilization (%)"]
            memory.columns = ["Container Memory Utilization (%)"]
            startup_latency.columns = ["Container Startup Latency (ms)"]
            for col in requests_count.columns:
                requests_count.rename(columns={col: "http code" + str(col)})
            for i in range(len(requests_latencies.columns)):
                if i != 0:
                    requests_latencies.iloc[:, 0] += requests_latencies.iloc[:, i]
            requests_latencies = requests_latencies.drop(requests_latencies.columns[1:], axis=1)
            requests_latencies.columns = ["Request Latency (ms)"]
        else:
            files = os.listdir(datasetpath)
            for f in files:
                temp = pd.read_csv(datasetpath + f)
                if f == "Container CPU Utilization.csv":
                    cpu = temp
                    cpu.set_index(temp.columns[0], inplace=True,drop=True)
                elif f == "Container Memory Utilization.csv":
                    memory = temp
                    memory.set_index(temp.columns[0], inplace=True,drop=True)
                elif f == "Container Startup Latency.csv":
                    startup_latency = temp
                    startup_latency.set_index(temp.columns[0], inplace=True,drop=True)
                elif f == "Instance Count.csv":
                    instance = temp
                    instance.set_index(temp.columns[0], inplace=True,drop=True)
                elif f == "Request Count.csv":
                    requests_count = temp
                    requests_count.set_index(temp.columns[0], inplace=True,drop=True)
                    for col in requests_count.columns:
                        if "1" in col:
                            requests_count.rename(columns={col: "http code 1xx"})
                        if "2" in col:
                            requests_count.rename(columns={col: "http code 2xx"})
                        if "3" in col:
                            requests_count.rename(columns={col: "http code 3xx"})
                        if "4" in col:
                            requests_count.rename(columns={col: "http code 4xx"})
                        if "5" in col:
                            requests_count.rename(columns={col: "http code 5xx"})
                elif f == "Request Latency.csv":
                    requests_latencies = temp
                    requests_latencies.set_index(temp.columns[0], inplace=True)

        columns_dict = {}
        columns_dict["instance"] = instance.columns
        columns_dict["cpu"] = cpu.columns
        columns_dict["memory"] = memory.columns
        columns_dict["start"] = startup_latency.columns
        columns_dict["request_count"] = requests_count.columns
        columns_dict["request_latencies"] = requests_latencies.columns
        data = pd.concat(
            [instance, cpu, memory, startup_latency, requests_latencies, requests_count], ignore_index=False, axis=1
        )
        data = data.fillna(0)
        # CPU utilization >= 60%
        self.cpu_limit_detection(data=data, col_class=columns_dict)
        print("cpu")
        # Memory utilization >= 60%
        self.memory_limit_detection(data=data, col_class=columns_dict)
        print("memory")
        # Cloud run re-start (startup_latency != 0)
        self.cloud_run_restart_detection(data=data, col_class=columns_dict)
        print("cloud run")
        # Instance count >= 2
        self.instance_count_detection(data=data, col_class=columns_dict)
        print("instance_count")
        # Fail Response
        self.request_fail(data=data, col_class=columns_dict)
        print("request_fail")
        return self.anomaly_log