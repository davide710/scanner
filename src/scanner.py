import cv2
from math import dist
import numpy as np

from debug import _resize, show_img, debug_threshold, show_contours
from preprocess import white, hsv_saturation
from postprocess import custom_threshold, with_cv2_functions

# size of A4 sheet in pixel:
a4_x = 2480
a4_y = 3508

postprocess_function = with_cv2_functions

def reorder(points): #cv2.findContours detects corners in random order, but to apply perspective you need them ordered
    lista = [[x[0][0], x[0][1]] for x in points]
    lista.sort(key=lambda x: x[1])
    a_and_b = lista[:2]
    a_and_b.sort(key=lambda x: x[0])
    a, b = a_and_b
    c_and_d = lista[2:]
    c_and_d.sort(key=lambda x: x[0])
    c, d = c_and_d
    distance_1 = dist(a, b)
    distance_2 = dist(a, c)

    # it's vertical
    if distance_1<=distance_2:
        return [a, b,
                c, d]
    # it's horizontal
    else:
        return [c, a,
                d, b]

def get_contours(img_gray):  # core function: detect the 4 corners of the document
    img_gray = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 199, 5)
    image = cv2.dilate(cv2.Canny(img_gray, 50, 50), None, 1)

    contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = list(contours)
    contours.sort(key=lambda x: cv2.contourArea(x))

    biggest = contours[-1]  # if everything worked, the biggest contour should be the document

    # Debug function call
    # show_contours(image, biggest)

    perimeter = cv2.arcLength(biggest, True)
    approx = cv2.approxPolyDP(biggest, 0.02*perimeter, True)

    if len(approx) == 4:
        return reorder(approx)
    else:
        return False

def scan_image(filepath, colorized):
    img = cv2.imread(filepath)

    if (contours:=get_contours(white(img))):
        pts1 = np.float32(contours)
    elif (contours:=get_contours(hsv_saturation(img))):
        pts1 = np.float32(contours)
    else: # i.e. if no document is detected
        print('ERROR!')
        print('No document detected!')
        print('Make shure the edges are easy to see (high contrast, no overlapping,...)')
        return False

    pts2 = np.float32([[0, 0], [a4_x, 0], [0, a4_y], [a4_x, a4_y]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)

    img_res_color = cv2.warpPerspective(img, matrix, (a4_x, a4_y))

    return postprocess_function(img_res_color, colorized)