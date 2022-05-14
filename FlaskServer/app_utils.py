import os
import requests
import random
import _thread as thread
from uuid import uuid4

import numpy as np
from PIL import Image

import base64
import io


def compress_image(image, path_original):
    size = 1920, 1080
    width = 1920
    height = 1080

    name = os.path.basename(path_original).split('.')
    first_name = os.path.join(os.path.dirname(path_original), name[0] + '.jpg')

    if image.size[0] > width and image.size[1] > height:
        image.thumbnail(size, Image.ANTIALIAS)
        image.save(first_name, quality=85)
    elif image.size[0] > width:
        wpercent = (width/float(image.size[0]))
        height = int((float(image.size[1])*float(wpercent)))
        image = image.resize((width,height), PIL.Image.ANTIALIAS)
        image.save(first_name,quality=85)
    elif image.size[1] > height:
        wpercent = (height/float(image.size[1]))
        width = int((float(image.size[0])*float(wpercent)))
        image = image.resize((width,height), Image.ANTIALIAS)
        image.save(first_name, quality=85)
    else:
        image.save(first_name, quality=85)


def convertToJPG(path_original):
    img = Image.open(path_original)
    name = os.path.basename(path_original).split('.')
    first_name = os.path.join(os.path.dirname(path_original), name[0] + '.jpg')

    if img.format == "JPEG":
        image = img.convert('RGB')
        compress_image(image, path_original)
        img.close()

    elif img.format == "GIF":
        i = img.convert("RGBA")
        bg = Image.new("RGBA", i.size)
        image = Image.composite(i, bg, i)
        compress_image(image, path_original)
        img.close()

    elif img.format == "PNG":
        try:
            image = Image.new("RGB", img.size, (255,255,255))
            image.paste(img,img)
            compress_image(image, path_original)
        except ValueError:
            image = img.convert('RGB')
            compress_image(image, path_original)
        
        img.close()

    elif img.format == "BMP":
        image = img.convert('RGB')
        compress_image(image, path_original)
        img.close()

def download(url, filename):
    data = requests.get(url).content
    with open(filename, 'wb') as handler:
        handler.write(data)

    return filename

def download_to_memory(url):

    r = requests.get(url)
    # return Image.open(StringIO(r.content))
    
    return Image.open(io.BytesIO(r.content))

def decode_base64_url(encoded_url):
    return base64.b64decode(encoded_url).decode('ascii')

def generate_random_filename(upload_directory, extension):
    filename = str(uuid4())
    filename = os.path.join(upload_directory, filename + "." + extension)
    return filename

def open_img_from_bytes(img_data):
    return Image.open(io.BytesIO(img_data)).convert("RGB")

def clean_me(filename):
    if os.path.exists(filename):
        os.remove(filename)

def clean_all(files):
    for me in files:
        clean_me(me)


def create_directory(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def get_model_bin(url, output_path):
    if not os.path.exists(output_path):
        create_directory(output_path)
        cmd = "wget -O %s %s" % (output_path, url)
        print(cmd)
        os.system(cmd)

    return output_path


#model_list = [(url, output_path), (url, output_path)]
def get_multi_model_bin(model_list):
    for m in model_list:
        thread.start_new_thread(get_model_bin, m)