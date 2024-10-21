import cv2
import numpy as np

def white(image):
    '''
    function that detects pixel that are supposed to be white
    i.e. pixels that have their B, G, and R values close enough
    and are bright enough
    '''
    im = np.array(image)

    im_reshaped = np.reshape(im, (-1, 3))
    dict = {'B': im_reshaped[:, 0], 'G': im_reshaped[:, 1], 'R': im_reshaped[:, 2]}

    means = np.mean(im_reshaped, axis=1)
    stdevs = np.std(im_reshaped, axis=1)

    dict['B'] = np.where(((stdevs < 10) & (means > 100)), 255, dict['B'])
    dict['G'] = np.where(((stdevs < 10) & (means > 100)), 255, dict['G'])
    dict['R'] = np.where(((stdevs < 10) & (means > 100)), 255, dict['R'])

    new = np.vstack((dict['B'], dict['G'], dict['R'])).T
    new = np.reshape(new, (im.shape[0], im.shape[1], 3))
    return cv2.cvtColor(new, cv2.COLOR_BGR2GRAY)

def hsv_saturation(image):
    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    saturation = hsv_img[:, :, 1] # get only saturation channel
    return saturation

