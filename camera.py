import cv2
import time
import random
import threading
import os
import numpy as np 
from PIL import Image
import dlib

print(" opencv version: ",cv2.__version__)
opencvDatapath = "/home/comx-admin/my360camera/my360cam/FlaskApp/opencvdata/haarcascades/"
faceCascade = cv2.CascadeClassifier(opencvDatapath + 'haarcascade_frontalface_default.xml')
folder = "/home/comx-admin/my360crm/static/"

class VideoCamera(object):
    def __init__(self):
        ipcam = "rtsp://admin:admin12345@192.168.0.199:554/Streaming/channels/2/"
        self.video = cv2.VideoCapture(0)
        self.detected_faces = []
        self.rectangleColor = (0,165,255)
        self.FPScount = 0
        self.currentFaceID = 0
        self.faceTrackers = {}
        self.faceNames = {}
        self.dlib_rect = []
        # self.video = cv2.VideoCapture(0)
        # width = self.video.set(3, 352)
        # height = self.video.set(4, 288)
        # print(width, height)
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self): 
        success, image = self.video.read()

        # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # uncomment to get gray image
        faces = faceCascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        for (x, y, w, h) in faces:
            rect = cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 1)
                      
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    # ------------------------------------ detect and tracking start -----------------------------------
    def doRecognizePerson(self, faceNames, fid):
        faceNames[ fid ] = "Person " + str(fid)
        print("face names in thread function :", faceNames)
        time.sleep(2)    

    def get_tracking_frame(self):
        FPScount = 0

        while True:
            success, image = self.video.read()
            FPScount += 1 
            print("########################", FPScount)
            fidsToDelete = []
            for fid in self.faceTrackers.keys():
                print("face trackers", self.faceTrackers)
                trackingQuality = self.faceTrackers[ fid ].update( image )

                if trackingQuality < 7:
                    fidsToDelete.append( fid )

            for fid in fidsToDelete:
                print("Removing fid " + str(fid) + " from list of trackers")
                self.faceTrackers.pop( fid , None )
        
            # if (FPScount % 10) == 0:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray, 1.3, 5)
            for (_x,_y,_w,_h) in faces:
                x = int(_x)
                y = int(_y)
                w = int(_w)
                h = int(_h)

                #calculate the centerpoint
                x_bar = x + 0.5 * w
                y_bar = y + 0.5 * h

                matchedFid = None

                for fid in self.faceTrackers.keys():
                    tracked_position =  self.faceTrackers[fid].get_position()
                    t_x = int(tracked_position.left())
                    t_y = int(tracked_position.top())
                    t_w = int(tracked_position.width())
                    t_h = int(tracked_position.height())

                    #calculate the centerpoint
                    t_x_bar = t_x + 0.5 * t_w
                    t_y_bar = t_y + 0.5 * t_h

                    if ( ( t_x <= x_bar   <= (t_x + t_w)) and 
                        ( t_y <= y_bar   <= (t_y + t_h)) and 
                        ( x   <= t_x_bar <= (x   + w  )) and 
                        ( y   <= t_y_bar <= (y   + h  ))):
                        matchedFid = fid
                        print(tracked_position)

                #If no matched fid, then we have to create a new tracker
                if matchedFid is None:
                    print("Creating new tracker " + str(self.currentFaceID))
                    tracker = dlib.correlation_tracker()

                    #----- to get the each detected face with x, y, w and h points to capture the face ----------
                    d_rect = dlib.rectangle( x-10, y-20, x+w+10, y+h+20)
                    self.dlib_rect.append(d_rect)
                    for r in self.dlib_rect:
                        print(r)
                        x = d_rect.left()
                        y = d_rect.top()
                        w = d_rect.right() - x
                        h = d_rect.bottom() - y
                        print(x, y, w, h)
                        crop_img = image[y: y + h, x: x + w]
                        cv2.imwrite( folder + "Person_" + str(self.currentFaceID) + ".jpg", crop_img)
                    # ----------------------- capturing detected face ended ----------------------------

                    tracker.start_track(image, dlib.rectangle( x-10, y-20, x+w+10, y+h+20))
                    self.faceTrackers[ self.currentFaceID ] = tracker
                    t = threading.Thread( target = self.doRecognizePerson, args=(self.faceNames, self.currentFaceID))
                    t.start()
                    # Increase the currentFaceID counter
                    self.currentFaceID += 1

            for fid in self.faceTrackers.keys():    
                tracked_position =  self.faceTrackers[fid].get_position()
                t_x = int(tracked_position.left())
                t_y = int(tracked_position.top())
                t_w = int(tracked_position.width())
                t_h = int(tracked_position.height())

                cv2.rectangle(image, (t_x, t_y), (t_x + t_w , t_y + t_h), self.rectangleColor ,2)

                if fid in self.faceNames.keys():
                    cv2.putText(image, self.faceNames[fid] , (int(t_x + t_w/2), int(t_y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                else:
                    cv2.putText(image, "Detecting...", (int(t_x + t_w/2), int(t_y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            ret, jpeg = cv2.imencode('.jpg', image)
            return jpeg.tobytes()

    #------------------------------------ detect and tracking end -----------------------------------


