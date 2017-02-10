#!/usr/bin/python



# Tutorial to start with: http://nummist.com/opencv/Howse_ISMAR_20140909.pdf

#TODO: Need to rotate test faces 

# Import the required modules
import cv2, os
import numpy as np
from PIL import Image
import json

# Path to the training faces
trainingPath = '../resources/known_faces/'
testPath = '../resources/test_faces/'

# For face detection we will use the Haar Cascade provided by OpenCV.
cascadePath = "../resources/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)

# For face recognition we will the the LBPH Face Recognizer 
recognizer = cv2.createLBPHFaceRecognizer()

nameArray = []

def indexFromName( name ):
    name = name.lower()

    if not( name in nameArray):
        nameArray.append( name )
    i = 0
    for n in nameArray:
        if n == name:
            return i
        i+=1
    raise Exception("Requested indexFromName not found: " + name)



def nameFromIndex( index ):
    if index < 0 or index > len(nameArray):
        raise Exception("Requested nameFromIndex not found: " + index)
    return nameArray[index]


def get_images_and_labels(path):

    image_paths = []

    for path, subdirs, files in os.walk(path):
        for name in files:
            fileType = name.split('.')[-1].lower()
            #print( fileType)
            if fileType in ['jpg', 'jpeg', 'png', 'gif']:
                image_paths.append( os.path.join(path, name) )

    # Append all the absolute image paths in a list image_paths
    # We will not read the image with the .sad extension in the training set
    # Rather, we will use them to test our accuracy of the training
    #image_paths = [os.path.join(path, f) for f in os.listdir(path) if not f.endswith('.DS_Store')]
    # images will contains face images
    images = []
    # labels will contains the label that is assigned to the image
    labels = []


    #print( image_paths )
    for image_path in image_paths:
        # Read the image and convert to grayscale
        image_pil = Image.open(image_path).convert('L')
        # Convert the image format into numpy array
        image = np.array(image_pil, 'uint8')
        # Get the label of the image
        #nbr = int(os.path.split(image_path)[1].split(".")[0].replace("subject", ""))
        person = os.path.split(image_path)[0].split("/")[-1]
        nbr = indexFromName( person )
        print( person )

        # Detect the face in the image
        faces = faceCascade.detectMultiScale(image)
        # If face is detected, append the face to images and the label to labels
        for (x, y, w, h) in faces:

            # Don't train on really small faces. We cropped the 
            # images to be the rigth size
            if w < image.shape[0] / 4:
                continue

            images.append(image[y: y + h, x: x + w])
            labels.append(nbr)
            cv2.imshow("Adding faces to traning set...", image[y: y + h, x: x + w])
            #cv2.waitKey(3000)
    # return the images list and labels list
    return images, labels


# Call the get_images_and_labels function and get the face images and the 
# corresponding labels
images, labels = get_images_and_labels(trainingPath)

cv2.destroyAllWindows()

# Save the mapping to people's names for later
with open( "../resources/recognizedfacesNames.json", 'w') as f:
    f.write( json.dumps(nameArray) )

# Perform the tranining
recognizer.train(images, np.array(labels))


image_paths = [os.path.join(testPath, f) for f in os.listdir(testPath) if f.endswith("png") ]
#image_paths = [f for f in os.listdir(testPath) if (f.endswith("png"))]

print("Testing Image paths: " + str( image_paths ) )

for image_path in image_paths:
    print( "\n\n\n" + image_path )
    predict_image_pil = Image.open(image_path).convert('L')
    predict_image = np.array(predict_image_pil, 'uint8')
    faces = faceCascade.detectMultiScale(predict_image)
    for (x, y, w, h) in faces:

        if w < 100:
            continue

        nbr_predicted, conf = recognizer.predict(predict_image[y: y + h, x: x + w])

        print( "Face: " + str(w) + " width " + str(h) + " height")
        print( "\tSubject Number Predicted: " + str(nbr_predicted) + " " + str(conf))
        print( "\tPredicted Person: " + nameFromIndex( nbr_predicted))
        name_actual = image_path.split("/")[-1].split(".")[0]
        nbr_actual = indexFromName(name_actual)
        if conf > 100:
            print("\tNo confidence in prediction: " + str(conf) )
        if nbr_actual == nbr_predicted:
            print ( "\t" + name_actual + " is Correctly Recognized with confidence " + str(conf))
        else:
            print( "\t" + name_actual + " is Incorrect Recognized as " + nameFromIndex(nbr_predicted) )
        cv2.imshow("Recognizing Face", predict_image[y: y + h, x: x + w])
        cv2.waitKey(1000)

# Save our recognition for later
recognizer.save('../resources/recognizedfaces.xml') 

