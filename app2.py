from flask import Flask, render_template, Response
from tracker import Tracker
import time
import threading
import cv2
import dlib
import threading
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.detectAndTrackMultipleFaces()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(Tracker()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_all_faces', methods = ['GET'])
def get_all_faces():
    return Tracker().get_all_faces()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
