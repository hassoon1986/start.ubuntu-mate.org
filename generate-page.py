#!/usr/bin/env python3

import sys
import os
import inspect
import glob
import shutil
import base64
import csscompressor        # Can be installed in python3-csscompressor package.

######################################
def load(path):
    f = open(path, "r")
    data = ""
    for line in f:
        data += line
    f.close()
    return data

def save(path, data):
    f = open(path, "w+")
    f.write(data)
    f.close()

######################################

def compress(filename):
    print("Compressing: " + filename)
    path = os.path.join(build_dir, filename)
    data = load(path)
    newdata = csscompressor.compress(data)
    save(path, newdata)

def strip(filename):
    print("Stripping: " + filename)
    path = os.path.join(build_dir, filename)
    data = load(path)
    newdata = ""
    for line in data.split('\n'):
        if line.startswith('/*') or len(line) == 0:
            continue
        line = line.replace(' > ','>')
        line = line.replace(': ',':')
        line = line.replace(' {','{')
        newdata += line.strip() + '\n'
    save(path, newdata)

def replace(filename, old, new):
    print("Replacing: " + filename)
    path = os.path.join(build_dir, filename)
    data = load(path)
    newdata = data.replace(old, new)
    save(path, newdata)

def convert_base64(filename):
    path = os.path.join(build_dir, filename)
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return(str(encoded_string))

######################################
cur_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
build_dir = os.path.join(cur_dir, "dist")

# Create target directory
if os.path.exists(build_dir):
    shutil.rmtree(build_dir)
os.mkdir(build_dir)
os.chdir(build_dir)

# Copy files to target
for ext in ["ico", "png", "html", "css", "js"]:
    path = glob.glob(cur_dir + '/*.' + ext)
    for file in path:
        print("Copying: " + file)
        shutil.copy(file, build_dir)

# Perform optimisation
# --> Compress Pages
compress("index.html")

strip("start.css")
replace("index.html", \
        '<link rel="stylesheet" type="text/css\" href="start.css">', \
        "<style>" + load("start.css") + "</style>")

strip("spritesheet.css")
replace("index.html", \
        '<link rel="stylesheet" type="text/css\" href="spritesheet.css">', \
        "<style>" + load("spritesheet.css") + "</style>")

compress("start.js")
replace("index.html", \
        '<script src="start.js"></script>', \
        "<script>" + load("start.js") + "</script>")

compress("locale.js")
replace("index.html", \
        '<script src="locale.js"></script>', \
        "<script>" + load("locale.js") + "</script>")
replace("index.html", "><", ">\n<")

# --> Embed Images
replace("index.html", 'favicon.ico', 'data:image/ico;base64,' + convert_base64("favicon.ico"))
replace("index.html", 'logo.png', 'data:image/png;base64,' + convert_base64("logo.png"))
replace("index.html", 'spritesheet.png', 'data:image/png;base64,' + convert_base64("spritesheet.png"))

# --> Clean up unused files
for ext in ["css", "ico", "png", "jpg", "js"]:
    path = glob.glob(build_dir + '/*.' + ext)
    for file in path:
        os.remove(file)
print("Finished!")
