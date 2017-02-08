import cv2
import sys
import scipy.misc

FACE_CASCADE_PATH = "../resources/haarcascade_frontalface_default.xml"
FACE_PROFILE_CASCADE_PATH = '../resources/haarcascade_profileface.xml'
EYE_CASCADE_PATH = cv2.CascadeClassifier("../resources/haarcascade_eye.xml")

faceCascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)
profileFaceCascade = cv2.CascadeClassifier(FACE_PROFILE_CASCADE_PATH)
video_capture = cv2.VideoCapture(0)

div = 0.25

while True:
    # Capture frame-by-frame
    ret, fullFrame = video_capture.read()
    frame = fullFrame
    #frame = cv2.resize(fullFrame, (fullFrame.shape[1]/div, fullFrame.shape[0]/div))

    frame = cv2.resize(fullFrame,None,fx=div, fy=div, interpolation = cv2.INTER_LINEAR)

    print("Full: " + str(fullFrame.shape))
    print("Small: " + str(frame.shape))

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(25, 25),
        flags=cv2.cv.CV_HAAR_SCALE_IMAGE
    )

    facesProfiles = profileFaceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(25, 25),
        flags=cv2.cv.CV_HAAR_SCALE_IMAGE
    )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        print("Face: " + str((x, y, w, h)))
        cv2.rectangle(fullFrame, (int(x/div), int(y/div)), (int(x/div+w/div), int(y/div+h/div)), (0, 255, 0), 4)

        roi_gray = gray[y:y+h, x:x+w]
        roi_color = fullFrame[int(y/div):int(y/div+h/div), int(x/div):int(x/div+w/div)]

        eyes = eye_cascade.detectMultiScale(roi_gray,
            scaleFactor=1.1,
            minNeighbors=2,
            minSize=(w/6, h/6),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )

        for (ex,ey,ew,eh) in eyes:
            cv2.rectangle(roi_color,(int(ex/div),int(ey/div)),(int(ex/div+ew/div),int(ey/div+eh/div)),(255,0,0),4)        

    # Display the resulting frame
    cv2.imshow('Video', fullFrame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()