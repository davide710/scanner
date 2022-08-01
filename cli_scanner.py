import sys
import os
import ntpath
import cv2
import numpy as np
from fpdf import FPDF 

foglio_x = 100 * 4
foglio_y = 140 * 4

def reorder(points):
    lista = [[x[0][0], x[0][1]] for x in points]
    xs = [x[0][0] for  x in points]
    ys = [x[0][1] for  x in points]
    b = (max(xs) + min(xs)) // 2
    h = (max(ys) + min(ys)) // 2
    if h > b: # è in verticale
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
        print('Usa una foto in orizzontale.')
        #sys.exit()
        return False

def get_contours(image):
    contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contorni = list(contours)
    contorni.sort(key=lambda x: cv2.contourArea(x))
    biggest = contorni[-1]
    perimeter = cv2.arcLength(biggest, True)
    approx = cv2.approxPolyDP(biggest, 0.02*perimeter, True)
    if len(approx) == 4:
        return reorder(approx)  #vertici_ordinati
    else:
        print('ERROR!')
        print('No document detected!')
        #sys.exit()
        return False

def scan_image(filepath, colorized):
    img = cv2.imread(filepath)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_canny = cv2.Canny(img_gray, 50, 50)

    if not get_contours(img_canny):
        return False

    pts1 = np.float32(get_contours(img_canny))
    pts2 = np.float32([[0, 0], [foglio_x, 0], [0, foglio_y], [foglio_x, foglio_y]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    if colorized:
        perspective_img = cv2.warpPerspective(img, matrix, (foglio_x, foglio_y), )
    else:
        perspective_img = cv2.warpPerspective(img_gray, matrix, (foglio_x, foglio_y), )
    return perspective_img[10:foglio_y-10, 10:foglio_x-10]

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
        print('Usage 1): python3 cli_scanner path/to/image [-c (colorized)]')
        print('Usage 2): python3 cli_scanner path/to/folder [-c (colorized)]')
        print('Usage 3): python3 cli_scanner . [-c (colorized)]')
        sys.exit()
