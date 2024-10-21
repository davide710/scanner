# DOCUMENT SCANNER

### Your pocket scanner: effortless A4 document capture and transformation into a clean PDF

### WHAT'S NEW

###### There's plenty of similar projects, what is it that makes this repository different (and better) ?

- it's purpose is to do _one_ thing, and to do it right
- lightweight (no heavy models), fast and super-easy to use
- the code detects pixels that are supposed to be white and makes them _white_, so that if you need to print the document you don't have to waste ink
- automatically scan all the images in a directory
- choose if you want the result to be colorized or black and white

![prova2](https://github.com/davide710/scanner/assets/106482229/19b6b4f5-96dd-4008-84d5-a2bb81693491)

![Screenshot from 2024-03-22 19-40-22](https://github.com/davide710/scanner/assets/106482229/d017f0bf-7800-4a43-ac22-322aa37a727a)



### USAGE

The photo must contain the 4 corners of the sheet (it will obviously work better if there's nothing else in the picture and if the quality is high), and it has to be vertical.
```
git clone https://github.com/davide710/scanner.git
pip install -r requirements.txt
```
```
python3 src/main.py path/to/image [-c (colorized)]
```
```
python3 src/main.py path/to/folder [-c (colorized)]
```
```
python3 src/main.py . [-c (colorized)]
```

If for some reason the sheet isn't detected, run the other script (replace main.py with test_and_others/doc_scan_click.py). This time the image will appear and you'll be clicking on the 4 corners of the document


The same code is behind https://onlinescanner.pythonanywhere.com/


### WANT TO HELP MAKING THIS BETTER?
I keep uploading many results, trying to show both examples of successful and failed tests and highlight pros and cons of the different ideas I get.
If you want to improve this, if you have an idea to make it better, or if you are having trouble using or setting this up, please raise an issue.
Otherwise, work on one of the improvements I mentioned in the Issues section.
You can also star the repository.
