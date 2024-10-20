import ntpath
import cv2
import numpy as np
from fpdf import FPDF
import os

filepath = 'examples/prova2.jpeg'#input('Path to file: ')
colorized = True

img = cv2.imread(filepath)
vertici = [] #list that will contain the four selected corner points

#print(img.shape)
initial_x = img.shape[1]
initial_y = img.shape[0]

ratio = 600 / initial_x

final_x = 600
final_y = int(initial_y * ratio)

foglio_x = 2480
foglio_y = 3508

img_resize = cv2.resize(img, (final_x, final_y))


def reorder(points):
    xs = [x[0] for  x in points]
    ys = [x[1] for  x in points]
    b = (max(xs) + min(xs)) // 2
    h = (max(ys) + min(ys)) // 2
    if h > b: # it's vertical
        points.sort(key=lambda x: x[1])
        a_e_b = points[:2]
        a_e_b.sort(key=lambda x: x[0])
        a = a_e_b[0]
        b = a_e_b[1]
        c_e_d = points[2:]
        c_e_d.sort(key=lambda x: x[0])
        c = c_e_d[0]
        d = c_e_d[1]
        return [a, b, c, d]
    else:
        print('Use an horizontal picture.')
        return False

def click(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN and len(vertici) < 4:
        vertici.append([int(x / ratio), int(y / ratio)])


while True:
    cv2.imshow('image', img_resize)

    cv2.setMouseCallback('image', click)

    if cv2.waitKey(1) & len(vertici) == 4:
        cv2.destroyAllWindows()
        break

def get_threshold(image, colorized):
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    for t in range(200, 120, -1):
        image_th = cv2.threshold(image_gray, t, 255, cv2.THRESH_BINARY)[1]
        rect = image_th[foglio_y-75:foglio_y-42, 72:foglio_x-72]
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

    pts1 = np.float32(reorder(vertici))
    pts2 = np.float32([[0, 0], [foglio_x, 0], [0, foglio_y], [foglio_x, foglio_y]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)

    img_res_color = cv2.warpPerspective(img, matrix, (foglio_x, foglio_y))
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

    return res[40:foglio_y-40, 40:foglio_x-40]


output_img = scan_image(filepath, colorized)

dir = os.path.join(os.getcwd(), 'scanned')
if not os.path.exists(dir):
    os.mkdir(dir)

cv2.imwrite('scanned/image_scanned.jpg', output_img)

pdf = FPDF(format='A4', unit='cm')
pdf.add_page()

pdf.image('scanned/image_scanned.jpg', 0, 0, 21, 29.7)
pdf.output(f"scanned/{ntpath.basename(filepath).split('.')[0]}.pdf", "F")
os.remove('scanned/image_scanned.jpg')
