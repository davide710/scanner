import cv2
import numpy as np

def _resize(img): #for debug purposes
    width = 400
    scale_factor = width / img.shape[1]
    height = int(img.shape[0] * scale_factor)
    dimension = (width, height)
    im = cv2.resize(img, dimension, interpolation = cv2.INTER_AREA)
    return im

def debug_threshold(img) -> int:
    '''
    Function opens image with a threshold slider to adjust it in real time.
    The inputed value effects the lower value [cv2.threshold(img, <VALUE>, 255, cv2.THRESH_BINARY)]
    '''
    # Callback function for the trackbar
    def update_threshold(threshold_value):
        _, thresholded_img = cv2.threshold(gray_img, threshold_value, 255, cv2.THRESH_BINARY)
        cv2.imshow('Thresholded Image', _resize(thresholded_img))

    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img

    # Create a window to display the image
    cv2.namedWindow('Thresholded Image')

    # Initialize threshold value
    threshold_value = 120

    # Create a trackbar
    cv2.createTrackbar('Threshold', 'Thresholded Image', threshold_value, 255, update_threshold)

    # Wait for ESC key to exit
    while cv2.getWindowProperty('Thresholded Image', cv2.WND_PROP_VISIBLE) >= 1:
        value = cv2.getTrackbarPos('Threshold', 'Thresholded Image')
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC key
            break

    # Close all windows
    cv2.destroyAllWindows()
    return value

def show_img(img):
    cv2.imshow("title", _resize(img))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def show_contours(image, biggest):
    """
    Gets the image to create a white background of the image size and the countour selected by the get_contours function (biggest).
    Shows the calculated outline of the document.
    """
    height, width = image.shape
    blank_image = np.ones((height, width), np.uint8) * 255
    show_img(cv2.drawContours(blank_image, biggest, -1, (0, 0, 0), 3))
