import cv2
import os
import time
import numpy as np
from matplotlib import pyplot as plt

def check_connection():
    """
    This function will check if the camera is open and is accessed by the system.
    It will return True or False as a success flag
    """
    if not cap.isOpened():
        raise IOError("Cannot access the camera - make sure that the port is open/it is plugged in")

    (ret, frame) = cap.read() # return a boolean (success flag) and an array corresponding to the color values of the frame you captured
    if ret:
        print("Successfully connected to the camera.")
        return ret

def takephoto(path):
    
    """
    This function takes a picture of the frame and saves it
    to the specified local path. The file name is in the form Capturea.jpg
    where a is the smaple test number. This is a required parameter for the function.
    """

    cap = cv2.VideoCapture(1)

    for i in range(50): #depending on how many experiments will be run
        ret, frame = cap.read()
        cv2.imwrite(os.path.join(path, 'capture' + str(i) + '.jpg'), frame)
        
        print('image captured')
        time.sleep(10) #will need to figure out the timing in between captures

    cap.release()


def disconnect():
    cap.release()
    print('disconnected')

def quantifygold():
    """
    This function outputs the percentage of non black and white pixels in the image provided in the pathway
    in order to quantify the amount of gold deposited on a GDL. 
    """
    path = input('please input the path for the image you are trying to analyze:')
    if type (path) != str:
        return None
    else:
        img = cv2.imread(str(path)) #0 for grayscale, 1 for color
        plt.imshow(img) 
        
        print('image shape: ' + str(img.shape))
        number_of_white_pix = np.sum(img == 255) #255 represents white pixels in the array when the image is in RGB
        number_of_black_pix = np.sum(img == 0) #0 is black value
        print('Number of white pixels:', number_of_white_pix)
        print('Number of black pixels:', number_of_black_pix)

        non_bw_pixels = img.size - number_of_white_pix - number_of_black_pix

        gold_dep = (non_bw_pixels/img.size)*100
        non_gold = ((number_of_white_pix + number_of_black_pix)/img.size)*100

        print('the percentage of pixels with gold deposited in this frame: ' + str(gold_dep) + ' %')
        print('the percentage of pixels without gold deposited in this frame: ' + str(non_gold) + ' %')
        print('checking:' + str (gold_dep + non_gold) + ' %')
        
        return gold_dep
