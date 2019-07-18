
from flask import Flask, render_template, Response
from camera import VideoCamera
import threading
import cv2
import dlib
import threading
import time, os
import detector
from flask_socketio import SocketIO, emit
from time import sleep
import requests, json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

folder = "/home/comx-admin/my360crm/static/capturedfaces/"
base_url = "https://internal.my360crm.com/website/190507150303DEMOCRM/shift/api/json/"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods = ['POST'] )
def home():
    return render_template('home.html')

def gen(camera):
    while True:
        frame = camera.get_tracking_frame() 
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@socketio.on('connect', namespace='/test')
def people_detected():
    people_data = []
    for filename in os.listdir(folder):
        files = {'image': open(folder + filename, 'rb')}
        json_response = requests.post(base_url + "aws.php", files=files)
        json_response =json_response.json()
        print(json_response)
        if json_response['status'] == "success":
            json_response['facename'] = filename
        else:
            json_response['facename'] = filename
            json_response['username'] = "Unknown"
        people_data.append(json_response)

    socketio.emit('people_detected', json.dumps(people_data), namespace='/test')
    sleep(2)



@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
    
