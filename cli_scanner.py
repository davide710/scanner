import sys
import os
import ntpath
import cv2
import numpy as np
from fpdf import FPDF 

####################### controlli
if len(sys.argv) ==  2:
    filepath = sys.argv[1]
    if filepath.split('.')[-1] not in ['jpg', 'jpeg', 'png']:
        print('ERROR')
        print('Unsupported format! Supported formats: .jpg, .jpeg, .png')
        sys.exit()
    if not os.path.exists(filepath):
        print('ERROR')
        print('File not found! Insert a valid path.')
        sys.exit()
else:
    print('ERROR')
    print('Usage: python3 cli_scanner path/to/image')
    sys.exit()
##############

img = cv2.imread(filepath)
vertici = []
initial_x = img.shape[1]
initial_y = img.shape[0]

foglio_x = 100 * 4
foglio_y = 140 * 4

img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img_canny = cv2.Canny(img_gray, 50, 50)

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
        sys.exit()

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
        sys.exit()
        
pts1 = np.float32(get_contours(img_canny))
pts2 = np.float32([[0, 0], [foglio_x, 0], [0, foglio_y], [foglio_x, foglio_y]])
matrix = cv2.getPerspectiveTransform(pts1, pts2)
perspective_img = cv2.warpPerspective(img_gray, matrix, (foglio_x, foglio_y), )

output_img = perspective_img[10:foglio_y-10, 10:foglio_x-10]

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
sys.exit()
