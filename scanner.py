import sys
import os
import ntpath
import cv2
import numpy as np
from fpdf import FPDF

a4_x = 2480
a4_y = 3508


def reorder(points):
    lista = [[x[0][0], x[0][1]] for x in points]
    xs = [x[0][0] for  x in points]
    ys = [x[0][1] for  x in points]
    b = (max(xs) + min(xs)) // 2
    h = (max(ys) + min(ys)) // 2
    if h > b: # it's vertical
        lista.sort(key=lambda x: x[1])
        a_e_b = lista[:2]
        a_e_b.sort(key=lambda x: x[0])
        a = a_e_b[0]
        b = a_e_b[1]
        c_e_d = lista[2:]
        c_e_d.sort(key=lambda x: x[0])
        c = c_e_d[0]
        d = c_e_d[1]
        return [a, b, c, d]
    else:
        print('Use an horizontal picture.')
        return False

def get_contours(image):
    contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contorni = list(contours)
    contorni.sort(key=lambda x: cv2.contourArea(x))
    biggest = contorni[-1]
    perimeter = cv2.arcLength(biggest, True)
    approx = cv2.approxPolyDP(biggest, 0.02*perimeter, True)
    if len(approx) == 4:
        return reorder(approx)
    else:
        print('ERROR!')
        print('No document detected!')
        return False

def get_threshold(image, colorized):
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    for t in range(200, 120, -1):
        image_th = cv2.threshold(image_gray, t, 255, cv2.THRESH_BINARY)[1]
        rect = image_th[a4_y-75:a4_y-42, 72:a4_x-72]
        whites = np.sum(rect == 255)
        blacks = np.sum(rect == 0)
        if whites != 0:
            if blacks / whites < 0.001:
                t = t if colorized else t - 10
                break
    return t

def scan_image(filepath, colorized):
    img = cv2.imread(filepath)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    th = cv2.threshold(img_gray,100,255,cv2.THRESH_OTSU+cv2.THRESH_BINARY)[1]

    if not get_contours(th):
        return False

    pts1 = np.float32(get_contours(th))
    pts2 = np.float32([[0, 0], [a4_x, 0], [0, a4_y], [a4_x, a4_y]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)

    img_res_color = cv2.warpPerspective(img, matrix, (a4_x, a4_y))
    img_res_gray = cv2.cvtColor(img_res_color, cv2.COLOR_BGR2GRAY)
    img_res_hsv = cv2.cvtColor(img_res_color, cv2.COLOR_BGR2HSV)
    threshold = get_threshold(img_res_color, colorized)

    if colorized:
        #mask = cv2.inRange(img_res_hsv, np.array([0, 0, threshold]), np.array([179, 255, 255]))
        #res = cv2.bitwise_not(img_res_color, img_res_color, mask)
        #res[mask == 255] = (255, 255, 255)
        mask = cv2.threshold(img_res_gray, threshold, 255, cv2.THRESH_BINARY)[1]
        img_res_color[mask == 255] = (255, 255, 255)
        res = img_res_color

    else:
        res = cv2.threshold(img_res_gray, threshold, 255, cv2.THRESH_BINARY)[1]
        
    return res[40:a4_y-40, 40:a4_x-40]

def to_pdf_and_save(output_img, filepath):
    dir = os.path.join(os.getcwd(), 'scanned')
    if not os.path.exists(dir):
        os.mkdir(dir)

    cv2.imwrite('scanned/image_scanned.jpg', output_img)

    pdf = FPDF(format='A4', unit='cm')
    pdf.add_page()
    pdf.image('scanned/image_scanned.jpg', 0, 0, 21, 29.7)
    filename = ntpath.basename(filepath).split('.')[0]
    pdf.output(f"scanned/{filename}.pdf", "F")
    os.remove('scanned/image_scanned.jpg')
    print('Scan saved in "scanned/" folder.')
    print()

def single_file_procedure(f_path, colorized):
    if f_path.split('.')[-1] not in ['jpg', 'jpeg', 'png']:
            print('Unsupported format! Supported formats: .jpg, .jpeg, .png')
    else:
        scan = scan_image(f_path, colorized)
        print(f_path)
        if not isinstance(scan, bool):
            to_pdf_and_save(scan, f_path)


if __name__ == '__main__':
    if len(sys.argv) ==  2 or (len(sys.argv) == 3 and sys.argv[2] == '-c'):
        file_path = sys.argv[1]
        condition = len(sys.argv) == 3

        if file_path == '.':
            files = [os.path.join(os.getcwd(), f) for f in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(), f))]
            if not files:
                print('ERROR!')
                print('No files were found.')
                sys.exit()
            for file in files:
                single_file_procedure(file, condition)
            sys.exit()

        if not os.path.exists(file_path):
            print('ERROR')
            print('File not found! Insert a valid path.')
            sys.exit()

        if os.path.isdir(file_path):
            files = [os.path.join(file_path, f) for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, f))]
            if not files:
                print('ERROR!')
                print('No files were found.')
                sys.exit()
            for file in files:
                single_file_procedure(file, condition)
            sys.exit()

        if os.path.isfile(file_path):
            single_file_procedure(file_path, condition)
            sys.exit()

    else:
        print('ERROR!')
        print('Usage 1): python3 scanner.py path/to/image [-c (colorized)]')
        print('Usage 2): python3 scanner.py path/to/folder [-c (colorized)]')
        print('Usage 3): python3 scanner.py . [-c (colorized)]')
        sys.exit()
