import numpy as np
import cv2

# size of A4 sheet in pixel:
a4_x = 2480
a4_y = 3508

def get_threshold(image, colorized):
    '''
    when applying cv2.threshold with a high value, many supposed to be white pixels become black.
    on the other hand, if the value is low it's likely that text or content will become white.
    that's why I think starting at 200 and going down is the best choice
    '''
    # value = debug_threshold(image)
    # return value
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    for t in range(200, 120, -1):  #try every threshold from 200 to 120 and check when enough pixels in rect are white
        image_th = cv2.threshold(image_gray, t, 255, cv2.THRESH_BINARY)[1]
        rect = image_th[a4_y-75:a4_y-42, 72:a4_x-72] # this region is often supposed to be white so it is a decent place to check
        whites = np.sum(rect == 255)
        blacks = np.sum(rect == 0)
        if whites == 0: continue
        if blacks / whites < 0.001:
            t = t if colorized else t - 10
            break
    return t

def custom_threshold(img_res_color, colorized):
    img_res_gray = cv2.cvtColor(img_res_color, cv2.COLOR_BGR2GRAY)

    threshold = get_threshold(img_res_color, colorized)

    if colorized:
        mask = cv2.threshold(img_res_gray, threshold, 255, cv2.THRESH_BINARY)[1]
        mask = cv2.bitwise_or(mask, cv2.adaptiveThreshold(img_res_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2))
        img_res_color[mask == 255] = (255, 255, 255)
        res = img_res_color

    else:
        res_1 = cv2.threshold(img_res_gray, threshold, 255, cv2.THRESH_BINARY)[1] #cv2.adaptiveThreshold(img_res_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        res_2 = cv2.adaptiveThreshold(img_res_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        res = cv2.bitwise_or(res_1, res_2)
        
    return res[40:a4_y-40, 40:a4_x-40]

def with_cv2_functions(img_res_color, colorized):
    img_res_gray = cv2.cvtColor(img_res_color, cv2.COLOR_BGR2GRAY)

    res_1 = cv2.adaptiveThreshold(img_res_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 199, 5)
    # run the image to filters to remove the noise
    res_2 = cv2.adaptiveThreshold(img_res_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 3)
    res_2 = cv2.erode(res_2, None, 1)
    res_2 = cv2.dilate(res_2, None, 1)
    res = cv2.bitwise_or(res_1, res_2)

    if not colorized: return res[40:a4_y-40, 40:a4_x-40]

    img_res_color[res == 255] = (255, 255, 255)
    res = img_res_color

    return res[40:a4_y-40, 40:a4_x-40]
