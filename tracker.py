import cv2
import dlib
import threading
import time
import os

print(" opencv version: ", cv2.__version__)

opencvDatapath = "/home/comx-admin/my360camera/my360cam/FlaskApp/opencvdata/haarcascades/"
faceCascade = cv2.CascadeClassifier(opencvDatapath + 'haarcascade_frontalface_default.xml')


class Tracker:
    """ tracker class to detect and track multiple faces in live streaming """

    def __init__(self):
        self.ipcam = "rtsp://admin:admin12345@192.168.0.199:554/Streaming/channels/2/"
        self.capture = cv2.VideoCapture(0)

    def get_all_faces(self):
        folder = "/home/comx-admin/my360crm/static"
        images = []
        for filename in os.listdir(folder):
            images.append(filename)
            print(filename)
        return images

    def doRecognizePerson(self, faceNames, fid):
        time.sleep(2)
        faceNames[ fid ] = "Person_" + str(fid)

    def detectAndTrackMultipleFaces(self):
        rectangleColor = (0,165,255)
        frameCounter = 0
        currentFaceID = 0
        faceTrackers = {}
        faceNames = {}
        cap_id = []

        ret, baseImage = self.capture.read()
        frameCounter += 1
        fidsToDelete = []
        for fid in faceTrackers.keys():
            trackingQuality = faceTrackers[ fid ].update( baseImage )
            if trackingQuality < 7:
                fidsToDelete.append( fid )
        for fid in fidsToDelete:
            print("Removing fid " + str(fid) + " from list of trackers")
            faceTrackers.pop( fid , None )
        if (frameCounter % 10) == 0:
            gray = cv2.cvtColor(baseImage, cv2.COLOR_BGR2GRAY)
            # faces = faceCascade.detectMultiScale(gray, 1.3, 5)
            faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            for (_x,_y,_w,_h) in faces:
                x = int(_x)
                y = int(_y)
                w = int(_w)
                h = int(_h)
                x_bar = x + 0.5 * w
                y_bar = y + 0.5 * h
                matchedFid = None
                for fid in faceTrackers.keys():
                    tracked_position =  faceTrackers[fid].get_position()
                    t_x = int(tracked_position.left())
                    t_y = int(tracked_position.top())
                    t_w = int(tracked_position.width())
                    t_h = int(tracked_position.height())
                    t_x_bar = t_x + 0.5 * t_w
                    t_y_bar = t_y + 0.5 * t_h
                    if ( ( t_x <= x_bar   <= (t_x + t_w)) and 
                            ( t_y <= y_bar   <= (t_y + t_h)) and 
                            ( x   <= t_x_bar <= (x   + w  )) and 
                            ( y   <= t_y_bar <= (y   + h  ))):
                        matchedFid = fid
                if matchedFid is None:
                    print("Creating new tracker " + str(currentFaceID))
                    tracker = dlib.correlation_tracker()
                    tracker.start_track(baseImage, dlib.rectangle( x-10, y-20, x+w+10, y+h+20))
                    faceTrackers[ currentFaceID ] = tracker
                    t = threading.Thread( target = self.doRecognizePerson, args=(faceNames, currentFaceID))
                    t.start()
                    currentFaceID += 1
        for fid in faceTrackers.keys():
            tracked_position =  faceTrackers[fid].get_position()
            t_x = int(tracked_position.left())
            t_y = int(tracked_position.top())
            t_w = int(tracked_position.width())
            t_h = int(tracked_position.height())
            cv2.rectangle(baseImage, (t_x, t_y), (t_x + t_w , t_y + t_h), rectangleColor, 1)
            if fid in faceNames.keys():
                cv2.putText(baseImage, faceNames[fid] , (int(t_x + t_w/2), int(t_y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                if (fid not in cap_id):
                    cap_id.append(fid)                     
                    crop_img = baseImage[y: y + h, x: x + w]
                    cv2.imwrite( "/home/comx-admin/my360crm/static/" + str(faceNames[fid]) + ".jpg", crop_img)
            else:
                cv2.putText(baseImage, "Detecting..." , (int(t_x + t_w/2), int(t_y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.imshow("result-image", baseImage)
        # ret, jpeg = cv2.imencode('.jpg', baseImage)
        # return jpeg.tobytes()

