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

def upload_img(transformed_img: Image) -> str:
    try:
        random_upload_filename = app_utils.generate_random_filename("", "jpg")
        upload_url = predictImg.FSDB.upload_img(transformed_img, random_upload_filename)
    except Exception as e:

        print(traceback.format_exc())
        return {"errors":"Output Image upload Error","message":"Could not upload image"}

    return upload_url

def transform_img(decoded_img: Image, render_factor: int=30, watermarked: bool=True) -> Image:
    
    transformed_img = predictImg.colorizer.get_transformed_image_from_memory(
                            decoded_img,
                            render_factor,
                            watermarked
    )
   
    return transformed_img

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


# class DeOldifyJITInferenceTask(current_app.Task):
#     # _FSDB = None
#     # _colorizer = None

#     # Method of persisting models for single workers from:
#     # https://stackoverflow.com/questions/19780821/in-python-celery-how-do-i-persist-objects-across-consecutive-worker-calls
#     def __init__(self):
        
#         self.pre_process_saved = torch.jit.load('scripted_models/pre_process.zip')
#         self.traced_model_saved = torch.jit.load('scripted_models/traced_model.zip')
#         self.post_process_saved = torch.jit.load('scripted_models/post_process.zip')

#         self.FSDB = app_database.FileStorage()

# def upload_img(transformed_img: Image) -> str:
#     try:
#         random_upload_filename = app_utils.generate_random_filename("", "jpg")
#         upload_url = JIT_predictImg.FSDB.upload_img(transformed_img, random_upload_filename)
#     except Exception as e:

#         print(traceback.format_exc())
#         return {"errors":"Output Image upload Error","message":"Could not upload image"}

#     return upload_url

# def JIT_colourize_image(decoded_img: Image, render_factor: int=30, watermarked: bool=True) -> Image:
    
#     from PIL import Image as PilImage
#     import PIL
#     import cv2

#     def _scale_to_square(orig: PilImage, targ: int) -> PilImage:
#         # a simple stretch to fit a square really makes a big difference in rendering quality/consistency.
#         # I've tried padding to the square as well (reflect, symetric, constant, etc).  Not as good!
#         targ_sz = (targ, targ)
#         return orig.resize(targ_sz, resample=PIL.Image.BILINEAR)

#     def _unsquare(image: PilImage, orig: PilImage) -> PilImage:
#         targ_sz = orig.size
#         image = image.resize(targ_sz, resample=PIL.Image.BILINEAR)
#         return image


#     def _post_process(raw_color: PilImage, orig: PilImage) -> PilImage:
#         color_np = np.asarray(raw_color)
#         orig_np = np.asarray(orig)
#         color_yuv = cv2.cvtColor(color_np, cv2.COLOR_BGR2YUV)
#         # do a black and white transform first to get better luminance values
#         orig_yuv = cv2.cvtColor(orig_np, cv2.COLOR_BGR2YUV)
#         hires = np.copy(orig_yuv)
#         hires[:, :, 1:3] = color_yuv[:, :, 1:3]
#         final = cv2.cvtColor(hires, cv2.COLOR_YUV2BGR)
#         final = PilImage.fromarray(final)
#         return final


#     # Use the original pre-processing pipeline with the traced model
#     norm, denorm = normalize_funcs(*imagenet_stats)

#     # Need to force conversion to grayscale otherwise the API finds it hard to decode color
#     grayify = decoded_img.convert('LA').convert('RGB')

#     model_image = _scale_to_square(grayify, 16*render_factor)
#     x = pil2tensor(model_image, np.float32)
#     x.div_(255)
#     x_pre_processed, y = norm((x, x), do_x=True)

#     filtered = JIT_predictImg.traced_model_saved(x_pre_processed[None,:].to('cuda:0'))

#     filtered = denorm(filtered, do_x=True).float().clamp(min=0, max=1)    # Why is this denormed twice?!

#     out = image2np(filtered[0,:].cpu().detach() * 255).astype(np.uint8)
#     filtered_img = PilImage.fromarray(out)

#     out_img = _post_process(_unsquare(filtered_img, decoded_img), decoded_img)


#     # Use the wholly torch based pre-processing pipeline
#     # x_tensor = pil2tensor(decoded_img, np.float32)[None,:]

#     # pre_processed = JIT_predictImg.pre_process_saved(x_tensor, 16*render_factor)
#     # filtered = JIT_predictImg.traced_model_saved(pre_processed.to('cuda:0'))
#     # out = JIT_predictImg.post_process_saved(filtered.cpu(), x_tensor)  

#     # Convert back to a PIL image for saving
#     # out_img = Image.fromarray(out[0,:].detach().numpy().astype(np.uint8))
    
    
#     return out_img

# @celery.task(base=DeOldifyJITInferenceTask, time_limit=500, serializer="pickle")
# def JIT_predictImg(bytes_encoded_img: bytes, render_factor: int=30, watermarked: bool=True):

#     gc.collect()

#     decoded_img = app_utils.open_img_from_bytes(bytes_encoded_img)
#     try:
#         transformed_img = JIT_colourize_image(decoded_img, render_factor, watermarked)
#     except Exception as e:
#         print(traceback.format_exc())
#         return {"errors":"Decolourisation Error", "message":str(e),
#             "stack_trace":str(traceback.format_exc()),
#         }
    
#     upload_url = upload_img(transformed_img)

#     gc.collect()

#     return {'status': 'OK', "decolourised_img_url": upload_url}