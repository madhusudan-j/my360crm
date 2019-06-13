
import cv2
import dlib
import threading
import time
import os, random

print("opencv version:", cv2.__version__)

opencvDatapath = "/home/comx-admin/my360camera/my360cam/FlaskApp/opencvdata/haarcascades/"
faceCascade = cv2.CascadeClassifier(opencvDatapath + 'haarcascade_frontalface_default.xml')

OUTPUT_SIZE_WIDTH = 775
OUTPUT_SIZE_HEIGHT = 600
folder = "/home/comx-admin/my360crm/static/"

def doRecognizePerson(faceNames, fid):
    time.sleep(1)
    faceNames[ fid ] = "Person_" + str(fid)
#     print(faceNames)

def detectAndTrackMultipleFaces():
    ipcam = "rtsp://admin:admin12345@192.168.0.199:554/Streaming/channels/2/"
    capture = cv2.VideoCapture(0)
    width = capture.set(3, 340)
    height = capture.set(4, 280)
    print(width, height)

    # cv2.namedWindow("base-image", cv2.WINDOW_AUTOSIZE) # to create frame
    cv2.namedWindow("result-image", cv2.WINDOW_AUTOSIZE)

    # cv2.moveWindow("base-image",0,100) # to fix position frame on screen
    cv2.moveWindow("result-image",400,100)

    #Start the window thread for the two windows we are using
    cv2.startWindowThread()

    #To set colour to rectangular box
    rectangleColor = (0,165,255)

    #variables holding the current frame number and the current faceid
    frameCounter = 0
    currentFaceID = 0

    #Variables holding the correlation trackers and the name per faceid
    faceTrackers = {}
    faceNames = {}
    dlib_rect = []

    try:
        while True:
            ret, baseImage = capture.read()
            # baseImage = cv2.resize( baseImage, ( 320, 240))

            pressedKey = cv2.waitKey(2)
            if pressedKey == ord('Q'):
                break
            resultImage = baseImage.copy()

            frameCounter += 1 

            fidsToDelete = []

            for fid in faceTrackers.keys():
                trackingQuality = faceTrackers[ fid ].update( baseImage )

                if trackingQuality < 7:
                    fidsToDelete.append( fid )

            for fid in fidsToDelete:
                print("Removing fid " + str(fid) + " from list of trackers")
                faceTrackers.pop( fid , None )

                for filename in os.listdir(folder):
                    if (str(fid) in str(filename)):
                        print(filename)
                        os.remove(folder + filename) 
                        
            #Every 10 frames, we will have to determine which faces
            #are present in the frame
            if (frameCounter % 10) == 0:
                
                gray = cv2.cvtColor(baseImage, cv2.COLOR_BGR2GRAY)
                faces = faceCascade.detectMultiScale(gray, 1.3, 5)

                for (_x,_y,_w,_h) in faces:
                    x = int(_x)
                    y = int(_y)
                    w = int(_w)
                    h = int(_h)

                    #calculate the centerpoint
                    x_bar = x + 0.5 * w
                    y_bar = y + 0.5 * h

                    #Variable holding information which faceid we 
                    #matched with
                    matchedFid = None

                    for fid in faceTrackers.keys():
                        tracked_position =  faceTrackers[fid].get_position()

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

                    #If no matched fid, then we have to create a new tracker
                    if matchedFid is None:

                        print("Creating new tracker " + str(currentFaceID))

                        #Create and store the tracker 
                        tracker = dlib.correlation_tracker()
                        d_rect = dlib.rectangle( x-10, y-20, x+w+10, y+h+20)
                        dlib_rect.append(d_rect)
                        for r in dlib_rect:
                            print(r)
                            x = d_rect.left()
                            y = d_rect.top()
                            w = d_rect.right() - x
                            h = d_rect.bottom() - y
                            print(x, y, w, h)
                            crop_img = resultImage[y: y + h, x: x + w]
                            cv2.imwrite( folder + "Person_" + str(currentFaceID) + ".jpg", crop_img)

                        tracker.start_track(baseImage, dlib.rectangle( x-10, y-20, x+w+10, y+h+20))

                        faceTrackers[ currentFaceID ] = tracker
                        print("############")
                        print("tracker ", tracker)
                        print("############")
                        print("facetrackers ",faceTrackers)
                        print("############")
                        print("facenames", faceNames)
                        print("############")
                        print("dlib obj type", type(faceTrackers[ currentFaceID ]))

                        t = threading.Thread( target = doRecognizePerson ,
                                               args=(faceNames, currentFaceID))
                        t.start()

                        #Increase the currentFaceID counter
                        currentFaceID += 1

            for fid in faceTrackers.keys():
                tracked_position =  faceTrackers[fid].get_position()

                t_x = int(tracked_position.left())
                t_y = int(tracked_position.top())
                t_w = int(tracked_position.width())
                t_h = int(tracked_position.height())
                cv2.rectangle(resultImage, (t_x, t_y),
                                        (t_x + t_w , t_y + t_h),
                                        rectangleColor ,2)
                # print("#########resultImage:",resultImage)
                if fid in faceNames.keys():
                    cv2.putText(resultImage, faceNames[fid], (int(t_x + t_w/2), int(t_y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                else:
                    cv2.putText(resultImage, "Detecting..." , (int(t_x + t_w/2), int(t_y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            largeResult = cv2.resize(resultImage, (OUTPUT_SIZE_WIDTH,OUTPUT_SIZE_HEIGHT))
            # cv2.imshow("base-image", baseImage)
            cv2.imshow("result-image", resultImage)

    except KeyboardInterrupt as e:
        print(e)
        pass

    cv2.destroyAllWindows()
    exit(0)

if __name__ == '__main__':
    detectAndTrackMultipleFaces()
    

