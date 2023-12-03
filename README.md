# DOCUMENT SCANNER

### Easy document scanner with python and OpenCV

Transform a photo of an A4 document to a pdf. 

### WHAT'S NEW

###### There's plenty of similar projects, what is it that makes this repository different (and hopefully better) ?

- it's purpose is to do _one_ thing, and to do it right
- lightweight (no heavy models), fast and super-easy to use
- the code detects pixels that are supposed to be white and makes them _white_, so that if you need to print the document you don't have to waste ink
- automatically scan all the images in a directory
- choose if you want the result to be colorized or black and white


### USAGE

The photo must contain the 4 corners of the sheet (it will obviously work better if there's nothing else in the picture and if the quality is high), and it has to be vertical.
```
git clone https://github.com/davide710/scanner.git
pip install -r requirements.txt
```
```
python3 scanner.py path/to/image [-c (colorized)]
```
```
python3 scanner.py path/to/folder [-c (colorized)]
```
```
python3 scanner.py . [-c (colorized)]
```

If for some reason the sheet isn't detected, run the other script (replace scanner.py with doc_scan_click.py). This time the image will appear and you'll be clicking on the 4 corners of the document


The same code is behind https://onlinescanner.pythonanywhere.com/


### WANT TO HELP MAKING THIS BETTER?
If you want to improve this, if you have an idea to make it better, or if you are having trouble using or setting this up, please raise an issue.
You can also star the repository.
