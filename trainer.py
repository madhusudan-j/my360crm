import os
import cv2
import numpy as np 
from PIL import Image

recognizer = cv2.face.LBPHFaceRecognizer_create()
path = 'dataset'
def getImageWithId(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    print(imagePaths)
    faces = []
    Ids = []
    for imagePath in imagePaths:
        faceImage = Image.open(imagePath).convert('L')
        faceNp = np.array(faceImage, 'uint8')
        ID = int(os.path.split(imagePath)[-1].split('.')[1])
        faces.append(faceNp)
        Ids.append(ID)
        cv2.waitKey(10)

    print(Ids, faces)
    return Ids, faces

Ids, faces = getImageWithId(path)
recognizer.train(faces, np.array(Ids))
recognizer.save("recognizer/trainingdata.yml")
