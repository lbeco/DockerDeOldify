from celery import Celery, Task, registry, current_app

import fastai
from deoldify.visualize import *
from pathlib import Path
import traceback
import os

import app_utils

from PIL import Image

import app_database
import app_utils

from app import celery

import torch
from fastai.vision.image import pil2tensor
import numpy as np

import gc

class DeOldifyInferenceTask(current_app.Task):
    # _FSDB = None
    # _colorizer = None

    # Method of persisting colourizer for single workers from:
    # https://stackoverflow.com/questions/19780821/in-python-celery-how-do-i-persist-objects-across-consecutive-worker-calls
    def __init__(self):
        self.colorizer = get_azure_artistic_image_colorizer()
        self.FSDB = app_database.FileStorage()

@celery.task()
def hello_world():
    print("Hello World")

def download_img(decoded_url: str) -> Image:
    img_to_be_encoded = app_utils.download_to_memory(decoded_url)

    try:
        img_to_be_encoded.copy().verify()
    except:
        return {"errors":"Download Image Error", "message":"Downloaded file is not an image!"}

    return img_to_be_encoded

def transform_img(decoded_img: Image, render_factor: int=30, watermarked: bool=True) -> Image:
    
    transformed_img = predictImg.colorizer.get_transformed_image_from_memory(
                            decoded_img,
                            render_factor,
                            watermarked
    )
   
    return transformed_img

def upload_img(transformed_img: Image) -> str:
    try:
        random_upload_filename = app_utils.generate_random_filename("", "jpg")
        upload_url = predictImg.FSDB.upload_img(transformed_img, random_upload_filename)
    except Exception as e:

        print(traceback.format_exc())
        return {"errors":"Output Image upload Error","message":"Could not upload image"}

    return upload_url

@celery.task(base=DeOldifyInferenceTask, time_limit=500, serializer="pickle")
def predictImg(bytes_encoded_img: bytes, render_factor: int=30, watermarked: bool=True):

    decoded_img = app_utils.open_img_from_bytes(bytes_encoded_img)
    try:
        transformed_img = transform_img(decoded_img, render_factor, watermarked)
    except Exception as e:
        print(traceback.format_exc())
        return {"errors":"Decolourisation Error", "message":str(e)}
    
    upload_url = upload_img(transformed_img)
    return {'status': 'OK', "decolourised_img_url": upload_url}


@celery.task(base=DeOldifyInferenceTask, time_limit=500, serializer="pickle")
def predictImgURL(decoded_url: str, render_factor: int = 30, watermarked: bool = True):
    
    img_to_be_encoded = download_img(decoded_url)

    # try:
    #     app_utils.download_to_memory(url)
    # except:
    #     # Generate random path
    #     input_path = app_utils.generate_random_filename(upload_directory,"jpeg")
    #     app_utils.download(url, input_path)
    #     app_utils.convertToJPG(input_path)

    transformed_img = transform_img(img_to_be_encoded, render_factor, watermarked)
    upload_url = upload_img(transformed_img)

    return {'status': 'OK', "decolourised_img_url": upload_url}