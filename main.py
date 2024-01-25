import json
import os
import threading
import time

from flask import Flask, request
from flask_cors import CORS

from systemctl import Controller

controller = Controller()
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


# auto detection thread
class Detector(threading.Thread):
    def __init__(self):
        super(Detector, self).__init__()
        self.stop_signal = threading.Event()

    def run(self):
        while not self.stop_signal.is_set():
            anomaly_log = str(controller.anomaly_detection(days=1, hours=0, minutes=5))
            error_code = controller.classification_anomlay(inputdata=anomaly_log)
            print(error_code)
            action = controller.real_detection(error_code)
            if "nothing to do" not in action:
                instruction(action)
            time.sleep(180)

    def stop(self):
        self.stop_signal.set()


detector = Detector()


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


def instruction(query):
    """get instruction code and implement action

    Args:
        query (_type_): command

    Returns:
        _type_: result of the action
    """
    output = ""
    # request_body: dict[str, str] = request.json
    # query = str(request_body["query"])
    # send query get instruction_code (e.g 1: chat , 2: detection, 3: analyze, 4: cpu up scale, 5: memory up scale)
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
        anomaly_log = str(controller.anomaly_detection(days=int(arg1), hours=int(arg2), minutes=int(arg3)))
        output = controller.analyze_data(anomaly_log)
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
        else:
            memory = controller.memory + 256
        status = controller.memory_up_scale(memory=memory)
        if status:
            output = str(arg1) + " memory finish"
        else:
            output = str(arg1) + "memory fail"
    elif instruction_code == 5:
        if str(arg1) == "stop":
            detector.stop()
        else:
            detector.start()
        output = str(arg1) + "auto detection"

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

    # return instruction(query=query)
    try:
        return instruction(query=query)
    except Exception as e:
        print(f"Failed to process query {query} with error {e}")
        return


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=port)
