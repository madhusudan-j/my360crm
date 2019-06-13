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

class VideoCamera(object):
    def __init__(self):
        ipcam = "rtsp://admin:admin12345@192.168.0.199:554/Streaming/channels/2/"
        self.video = cv2.VideoCapture(0)
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
#------------------------------------ detect and tracking start -----------------------------------

    #We are not doing really face recognition
    def doRecognizePerson(self, faceNames, fid):
        time.sleep(2)
        faceNames[ fid ] = "Person " + str(fid)

    def detectAndTrackMultipleFaces(self):
        OUTPUT_SIZE_WIDTH = 775
        OUTPUT_SIZE_HEIGHT = 600
        #Open the first webcame device
        ipcam = "rtsp://admin:admin12345@192.168.0.199:554/Streaming/channels/2/"
        capture = cv2.VideoCapture(0)
        # print(width, height)
        # width = cap.set(3, 352)
        # height = cap.set(4, 288)
        # print(width, height)

        #Create two opencv named windows
        # cv2.namedWindow("base-image", cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow("result-image", cv2.WINDOW_AUTOSIZE)

        #Position the windows next to eachother
        # cv2.moveWindow("base-image",0,100)
        cv2.moveWindow("result-image",400,100)

        #Start the window thread for the two windows we are using
        cv2.startWindowThread()

        #The color of the rectangle we draw around the face
        rectangleColor = (0,165,255)

        #variables holding the current frame number and the current faceid
        frameCounter = 0
        currentFaceID = 0

        #Variables holding the correlation trackers and the name per faceid
        faceTrackers = {}
        faceNames = {}

        try:
            while True:
                #Retrieve the latest image from the webcam
                ret, fullSizeBaseImage = capture.read()

                #Resize the image to 320x240
                baseImage = cv2.resize( fullSizeBaseImage, ( 320, 240))

                #Check if a key was pressed and if it was Q, then break
                #from the infinite loop
                pressedKey = cv2.waitKey(2)
                if pressedKey == ord('Q'):
                    break

                #Result image is the image we will show the user, which is a
                #combination of the original image from the webcam and the
                #overlayed rectangle for the largest face
                resultImage = baseImage.copy()

                #STEPS:
                # * Update all trackers and remove the ones that are not 
                #   relevant anymore
                # * Every 10 frames:
                #       + Use face detection on the current frame and look
                #         for faces. 
                #       + For each found face, check if centerpoint is within
                #         existing tracked box. If so, nothing to do
                #       + If centerpoint is NOT in existing tracked box, then
                #         we add a new tracker with a new face-id

                #Increase the framecounter
                frameCounter += 1 

                #Update all the trackers and remove the ones for which the update
                #indicated the quality was not good enough
                fidsToDelete = []
                for fid in faceTrackers.keys():
                    trackingQuality = faceTrackers[ fid ].update( baseImage )

                    #If the tracking quality is good enough, we must delete
                    #this tracker
                    if trackingQuality < 7:
                        fidsToDelete.append( fid )

                for fid in fidsToDelete:
                    print("Removing fid " + str(fid) + " from list of trackers")
                    faceTrackers.pop( fid , None )

                #Every 10 frames, we will have to determine which faces
                #are present in the frame
                if (frameCounter % 10) == 0:

                    #For the face detection, we need to make use of a gray
                    #colored image so we will convert the baseImage to a
                    #gray-based image
                    gray = cv2.cvtColor(baseImage, cv2.COLOR_BGR2GRAY)

                    #Now use the haar cascade detector to find all faces
                    #in the image
                    faces = faceCascade.detectMultiScale(gray, 1.3, 5)

                    #Loop over all faces and check if the area for this
                    #face is the largest so far
                    #We need to convert it to int here because of the
                    #requirement of the dlib tracker. If we omit the cast to
                    #int here, you will get cast errors since the detector
                    #returns numpy.int32 and the tracker requires an int
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

                        #Now loop over all the trackers and check if the 
                        #centerpoint of the face is within the box of a 
                        #tracker
                        for fid in faceTrackers.keys():
                            tracked_position =  faceTrackers[fid].get_position()

                            t_x = int(tracked_position.left())
                            t_y = int(tracked_position.top())
                            t_w = int(tracked_position.width())
                            t_h = int(tracked_position.height())


                            #calculate the centerpoint
                            t_x_bar = t_x + 0.5 * t_w
                            t_y_bar = t_y + 0.5 * t_h

                            #check if the centerpoint of the face is within the 
                            #rectangleof a tracker region. Also, the centerpoint
                            #of the tracker region must be within the region 
                            #detected as a face. If both of these conditions hold
                            #we have a match
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
                            tracker.start_track(baseImage,
                                                dlib.rectangle( x-10,
                                                                y-20,
                                                                x+w+10,
                                                                y+h+20))

                            faceTrackers[ currentFaceID ] = tracker

                            #Start a new thread that is used to simulate 
                            #face recognition. This is not yet implemented in this
                            #version :)
                            t = threading.Thread( target = VideoCamera().doRecognizePerson ,
                                                args=(faceNames, currentFaceID))
                            t.start()

                            #Increase the currentFaceID counter
                            currentFaceID += 1

                #Now loop over all the trackers we have and draw the rectangle
                #around the detected faces. If we 'know' the name for this person
                #(i.e. the recognition thread is finished), we print the name
                #of the person, otherwise the message indicating we are detecting
                #the name of the person
                for fid in faceTrackers.keys():
                    tracked_position =  faceTrackers[fid].get_position()

                    t_x = int(tracked_position.left())
                    t_y = int(tracked_position.top())
                    t_w = int(tracked_position.width())
                    t_h = int(tracked_position.height())

                    cv2.rectangle(resultImage, (t_x, t_y),
                                            (t_x + t_w , t_y + t_h),
                                            rectangleColor ,2)

                    if fid in faceNames.keys():
                        cv2.putText(resultImage, faceNames[fid] , 
                                    (int(t_x + t_w/2), int(t_y)), 
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.5, (255, 255, 255), 2)
                        crop_img = resultImage[y: y + h, x: x + w]
                        cv2.imwrite( "/home/comx-admin/my360crm/static/" + str(faceNames[fid]) + ".jpg", crop_img)
                    else:
                        cv2.putText(resultImage, "Detecting..." , 
                                    (int(t_x + t_w/2), int(t_y)), 
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.5, (255, 255, 255), 2)

                #Since we want to show something larger on the screen than the
                #original 320x240, we resize the image again
                #
                #Note that it would also be possible to keep the large version
                #of the baseimage and make the result image a copy of this large
                #base image and use the scaling factor to draw the rectangle
                #at the right coordinates.

                #to get larger size result uncomment below
                # largeResult = cv2.resize(resultImage,
                #                         (OUTPUT_SIZE_WIDTH, OUTPUT_SIZE_HEIGHT))

                #Finally, we want to show the images on the screen
                # cv2.imshow("base-image", baseImage)
                cv2.imshow("result-image", resultImage)

        #To ensure we can also deal with the user pressing Ctrl-C in the console
        #we have to check for the KeyboardInterrupt exception and break out of
        #the main loop
        except KeyboardInterrupt as e:
            pass

        #Destroy any OpenCV windows and exit the application
        cv2.destroyAllWindows()
        exit(0)

#------------------------------------ detect and tracking end -----------------------------------


