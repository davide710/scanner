from sys import argv, exit
import os
from ntpath import basename
import cv2
from math import dist
import numpy as np
from fpdf import FPDF
from debug import _resize, show_img, debug_threshold, show_contours

# size of A4 sheet in pixel:
a4_x = 2480
a4_y = 3508

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
    return new

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

def scan_image(filepath, colorized):
    img = cv2.imread(filepath)
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    saturation = hsv_img[:, :, 1] # get only saturation channel

    if (contours:=get_contours(saturation)):  # i.e. if no document is detected
        pts1 = np.float32(contours)
    elif (contours:=get_contours(cv2.cvtColor(white(img), cv2.COLOR_BGR2GRAY))):
        pts1 = np.float32(contours)
    else:
        print('ERROR!')
        print('No document detected!')
        print('Make shure the edges are easy to see (high contrast, no overlapping,...)')
        return False

    pts2 = np.float32([[0, 0], [a4_x, 0], [0, a4_y], [a4_x, a4_y]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)

    img_res_color = cv2.warpPerspective(img, matrix, (a4_x, a4_y))
    img_res_gray = cv2.cvtColor(img_res_color, cv2.COLOR_BGR2GRAY)
    img_res_hsv = cv2.cvtColor(img_res_color, cv2.COLOR_BGR2HSV)

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

def to_pdf_and_save(output_img, filepath):
    dir = os.path.join(os.getcwd(), 'scanned')
    if not os.path.exists(dir):
        os.mkdir(dir)

    cv2.imwrite('scanned/image_scanned.jpg', output_img)

    pdf = FPDF(format='A4', unit='cm')
    pdf.add_page()
    pdf.image('scanned/image_scanned.jpg', 0, 0, 21, 29.7)
    filename = basename(filepath).split('.')[0]
    pdf.output(f"scanned/{filename}.pdf", "F")
    os.remove('scanned/image_scanned.jpg')
    print('Scan saved in "scanned/" folder.\n')

def single_file_procedure(f_path, colorized):
    if f_path.split('.')[-1] not in ['jpg', 'jpeg', 'png']:
            print('Unsupported format! Supported formats: .jpg, .jpeg, .png')
    else:
        scan = scan_image(f_path, colorized)
        print(f_path)
        if not isinstance(scan, bool):
            to_pdf_and_save(scan, f_path)


if __name__ == '__main__':
    help_msg = '''
ERROR!
Usage 1): python3 scanner.py path/to/image [-c (colorized)]
Usage 2): python3 scanner.py path/to/folder [-c (colorized)]
Usage 3): python3 scanner.py . [-c (colorized)]
'''

    condition = len(argv) == 3 and argv[2] == '-c'
    if not (len(argv) ==  2 or condition):
        print(help_msg)
        exit()

    file_path = argv[1]

    if not os.path.exists(file_path):
        print('ERROR\nFile not found! Insert a valid path.')
        exit()

    if os.path.isfile(file_path):
        single_file_procedure(file_path, condition)
        exit()

    # DIRECTORY LOGIC
    def load_files_and_run_prog(path: str) -> list:
        files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        if not files:
            print('ERROR!\nNo files were found.')
            exit()
        for file in files:
            single_file_procedure(file, condition)
        exit()

    if file_path == '.':
        load_files_and_run_prog(os.getcwd())
    else:
        load_files_and_run_prog(file_path)
