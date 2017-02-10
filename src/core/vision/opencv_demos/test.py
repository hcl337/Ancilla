import cv2 as cv
import sys
import os, inspect
import scipy.misc
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from Faces import Faces

import logging
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)



print("\n\n\n\n\n" + str(Faces().detect( cv.imread( "../../Latest_Environment_Image.jpg"))) +"\n\n\n\n\n\n")
