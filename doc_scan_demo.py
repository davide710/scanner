import cv2
import numpy as np
from fpdf import FPDF 

img = cv2.imread('risorse/pagella2.jpeg')
vertici = []

#print(img.shape)
initial_x = img.shape[1]
initial_y = img.shape[0]

final_x = initial_x #// 3
final_y = initial_y #// 3

foglio_x = 100 * 4
foglio_y = 140 * 4

img_resize = cv2.resize(img, (final_x, final_y))
img_gray = cv2.cvtColor(img_resize, cv2.COLOR_BGR2GRAY)
img_canny = cv2.Canny(img_gray, 50, 50)

def reorder(points):
    lista = [[x[0][0], x[0][1]] for x in points]
    #print(lista)
    #lista2 = [[x[0][0], x[0][1]] for x in points]
    xs = [x[0][0] for  x in points]
    ys = [x[0][1] for  x in points]
    b = (max(xs) + min(xs)) // 2
    h = (max(ys) + min(ys)) // 2
    if h > b: # è in verticale
        #a_e_b = lista.sort(key=lambda x: -x[1])[:2]
        lista.sort(key=lambda x: x[1])
        a_e_b = lista[:2]
        #print(a_e_b)
        a_e_b.sort(key=lambda x: x[0])
        a = a_e_b[0]
        b = a_e_b[1]
        #print(a)
        #print(b)
        c_e_d = lista[2:]
        c_e_d.sort(key=lambda x: x[0])
        c = c_e_d[0]
        d = c_e_d[1]
        #print(c)
        #print(d)
        return [a, b, c, d]
    else:
        print('usa una foto in orizzontale')
        return [[0,0], [10,0], [0,10], [10,10]]

def click(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN and len(vertici) < 4:
        vertici.append([x, y])

def get_contours(image):
    contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:
            cv2.drawContours(img_resize, cnt, -1, (255,0,0), 3)
            perimeter = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02*perimeter, True)
            #vertici_ordinati = [[approx[0][0][0], approx[0][0][1]], [approx[3][0][0], approx[3][0][1]], [approx[1][0][0], approx[1][0][1]], [approx[2][0][0], approx[2][0][1]]]
            #print(vertici_ordinati)
            #obj_con = len(approx)
            x, y, w, h = cv2.boundingRect(approx)
    return reorder(approx)  #vertici_ordinati

""" while True:
    cv2.imshow('image', img_resize)
    
    cv2.setMouseCallback('image', click)

    if cv2.waitKey(1) & len(vertici) == 4:
        break
 """

pts1 = np.float32(get_contours(img_canny)) #(vertici) #(get_contours(img_canny))
pts2 = np.float32([[0, 0], [foglio_x, 0], [0, foglio_y], [foglio_x, foglio_y]])
matrix = cv2.getPerspectiveTransform(pts1, pts2)
cv2.imshow('test', img_resize)
perspective_img = cv2.warpPerspective(img_gray, matrix, (foglio_x, foglio_y), )

output_img = perspective_img[10:foglio_y-10, 10:foglio_x-10]

cv2.imshow('output', output_img)

cv2.imwrite('scanned/image_scanned.jpg', output_img)

pdf = FPDF(format='A4', unit='cm')
pdf.add_page()
#pdf.oversized_images = "DOWNSCALE"
pdf.image('scanned/image_scanned.jpg', 0, 0, 21, 29.7)
pdf.output("scanned/document_scanned.pdf", "F")

cv2.waitKey(0)

cv2.destroyAllWindows()