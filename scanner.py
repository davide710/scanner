import sys
import os
import ntpath
import cv2
import numpy as np
from fpdf import FPDF


# size of A4 sheet in pixel:
a4_x = 2480
a4_y = 3508

def _resize(img): #for debug purposes
    width = 400
    scale_factor = width / img.shape[1]
    height = int(img.shape[0] * scale_factor)
    dimension = (width, height)
    im = cv2.resize(img, dimension, interpolation = cv2.INTER_AREA)
    return im


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

def white(image): # function that detects pixel that are supposed to be white
                  # i.e. pixels that have their B, G, and R values close enough
                  # and are bright enough
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

    image = cv2.dilate(cv2.Canny(img_gray, 50, 50), None, 1)

    #image = cv2.threshold(img_gray, 130, 255, cv2.THRESH_OTSU+cv2.THRESH_BINARY)[1]

    contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours = list(contours)
    contours.sort(key=lambda x: cv2.contourArea(x))

    biggest = contours[-1]  # if everything worked, the biggest contour should be the document

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
    for t in range(200, 120, -1):  #try every threshold from 200 to 120 and check when enough pixels in rect are white 
        image_th = cv2.threshold(image_gray, t, 255, cv2.THRESH_BINARY)[1]
        rect = image_th[a4_y-75:a4_y-42, 72:a4_x-72] # this region is often supposed to be white so it is a decent place to check 
        whites = np.sum(rect == 255)
        blacks = np.sum(rect == 0)
        if whites != 0:
            if blacks / whites < 0.001: # when applying cv2.threshold with a high value, many supposed to be white pixels become black.
                                        # on the other hand, if the value is low it's likely that text or content will become white.
                                        # that's why I think starting at 200 and going down is the best choice
                t = t if colorized else t - 10
                break
    return t

def scan_image(filepath, colorized):
    img = cv2.imread(filepath)
    whited = white(img)
    img_gray = cv2.cvtColor(whited, cv2.COLOR_BGR2GRAY)


    if not get_contours(img_gray):  # i.e. if no document is detected
        return False

    pts1 = np.float32(get_contours(img_gray))
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

    else: #TODO: find a way to mix good aspects of adaptiveThreshold and of my custom method
        res_1 = cv2.threshold(img_res_gray, threshold, 255, cv2.THRESH_BINARY)[1] #cv2.adaptiveThreshold(img_res_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        res_2 = cv2.adaptiveThreshold(img_res_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        res = cv2.bitwise_or(res_1, res_2)
        
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
