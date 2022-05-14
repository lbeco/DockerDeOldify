import requests
import glob
import base64
import json

import os 

current_dir_path = os.path.dirname(os.path.realpath(__file__))
img_dir = os.path.join(current_dir_path, "test_images")
output_img_dir = os.path.join(current_dir_path, "output_images")

current_url = "https://colourize.cf/images/jitpredict"
old_url = "https://colourize.cf/images/oldpredict"

def send_request(url, encoded_img: str, render_factor: int = 30):
    payload = {"render_factor":render_factor,"encoded_img":encoded_img}
    payload = json.dumps(payload)

    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data = payload)

    return response

def get_img_as_b64encoded_str(img_filename):
    with open(img_filename, 'rb') as infile:
        return base64.b64encode(infile.read()).decode('ascii')

def test_response(response: requests.Response):
    print("Checking Response status code...")
    check = response.status_code == 200
    print(check)

    return check

def download_img_from_url(url: str, save_filename=None):
    url_filename = url.split('/')[-1]
    r = requests.get(url, allow_redirects=True)

    _, file_extension = os.path.splitext(url_filename)

    if save_filename is not None:
        filename = save_filename + file_extension
    else:
        filename = url_filename

    with open(filename, 'wb+') as outfile:
        outfile.write(r.content)

def test_url(url, encoded_img, save_filename):

    print(url)
    print("--------------------------")

    response = send_request(url, encoded_img)
    if test_response(response):
        colourised_img_url = response.json().get("decolourised_img_url", None)
        if colourised_img_url is not None:
            download_img_from_url(colourised_img_url, os.path.join(output_img_dir, save_filename))

    print( response.json() )

images = []
for ext in ["*.png", "*.jpg", "*.jpeg"]:
    images.extend(glob.glob(os.path.join(img_dir, ext)))


for image in images:
    encoded_img = get_img_as_b64encoded_str(image)

    test_url(current_url, encoded_img, "current")
    test_url(old_url, encoded_img, "old")

    



# url = "https://colourize.cf/images/jitpredict"

# payload = "{\n\t\"render_factor\":30,\n\t\"encoded_img\":\" \"\n\t}\n"
# headers = {
#   'Content-Type': 'application/json'
# }

# response = requests.request("POST", url, headers=headers, data = payload)

# print(response.text.encode('utf8'))
