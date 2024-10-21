from sys import argv, exit
import os
import cv2
from ntpath import basename
from fpdf import FPDF
from scanner import scan_image


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
Usage 1): python3 main.py path/to/image [-c (colorized)]
Usage 2): python3 main.py path/to/folder [-c (colorized)]
Usage 3): python3 main.py . [-c (colorized)]
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
