from sys import argv, exit
import os
from ntpath import basename
import cv2
import numpy as np
from fpdf import FPDF
from debug import _resize, show_img, debug_threshold, show_contours

# size of A4 sheet in pixel:
a4_x = 2480
a4_y = 3508

def reorder(points): #cv2.findContours detects corners in random order, but to apply perspective you need them ordered
    lista = [[x[0][0], x[0][1]] for x in points]
    #xs = [x[0][0] for  x in points]
    #ys = [x[0][1] for  x in points]
    #b = (max(xs) + min(xs)) // 2
    #h = (max(ys) + min(ys)) // 2
    lista.sort(key=lambda x: x[1])
    a_and_b = lista[:2]
    a_and_b.sort(key=lambda x: x[0])
    a = a_and_b[0]
    b = a_and_b[1]
    c_and_d = lista[2:]
    c_and_d.sort(key=lambda x: x[0])
    c = c_and_d[0]
    d = c_and_d[1]
    return [a, b, c, d]

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
    # use adaptive threshold before processing img
    img_gray = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 199, 5)
    image = cv2.dilate(cv2.Canny(img_gray, 50, 50), None, 1)
    #image = cv2.threshold(img_gray, 130, 255, cv2.THRESH_OTSU+cv2.THRESH_BINARY)[1]

    contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = list(contours)
    contours.sort(key=lambda x: cv2.contourArea(x))

    biggest = contours[-1]  # if everything worked, the biggest contour should be the document

    # Debug function call
    # show_contours(image, biggest)

    perimeter = cv2.arcLength(biggest, True)
    approx = cv2.approxPolyDP(biggest, 0.02*perimeter, True)
    print(len(approx))
    if len(approx) == 4:
        return reorder(approx)
    else:
        print('ERROR!')
        print('No document detected!')
        print('Make shure the edges are easy to see (high contrast, no overlapping,...)')
        return False

def scan_image(filepath, colorized):
    img = cv2.imread(filepath)
    whited = white(img)
    img_gray = cv2.cvtColor(whited, cv2.COLOR_BGR2GRAY)

    if not (contours:=get_contours(img_gray)):  # i.e. if no document is detected
        return False

    pts1 = np.float32(contours)
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
