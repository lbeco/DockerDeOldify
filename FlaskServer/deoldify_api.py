from flask_restx import Resource, Api, reqparse, inputs, fields, Namespace
from collections import OrderedDict
import base64

import app_utils


api = Namespace('images', description='DeOldify Inference API')

# Documentation for the API
output_error = api.model('error output', OrderedDict(
        errors=fields.String(
            description="Detailed Description of each error raised"),
        ),
        message=fields.String(
            description="comment on why Not OK")
        )

output_predict = api.model('Output from Predict', OrderedDict(
        status=fields.String(
            description="status of the request : OK/Not OK"),
        decolourised_img_url=fields.String(
            description="URL of where the output image was uploaded to")
        ))

def renderFactorType(value: str) -> int:
    '''Parse my type'''
    try:
        parsed_val = int(value)
    except:
        raise ValueError("{0} is not a valid integer!".format(value))

    if parsed_val < 7 or parsed_val > 45:
        raise ValueError('{0} is not constrained to be between 7 and 45!'.format(parsed_val))
    
    return parsed_val

def base64EncodedValueType(value: str) -> bytes:

    try:
        decoded = base64.b64decode(value)
    except:
        raise ValueError("{0} could not be base64 decoded successfully ><".format(decoded))

    return decoded

def base64EncodedURLType(value: str) -> str:

    url = base64EncodedValueType(value).decode('ascii')

    # try:
    #     url = app_utils.decode_base64_url(value)
    # except:
    #     raise ValueError("{0} could not be base64 decoded successfully ><".format(value))

    return inputs.URL(schemes=['http', 'https'])(url)

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('encoded_img_url', type=base64EncodedURLType, required=True, help='Base64 encoded version of the image URL to be decolourised. \n Can use this online service to generate URLs: https://www.base64encode.org/')
parser.add_argument('render_factor', type=renderFactorType, help="Render Factor. This should be an integer between 7 and 45.")
parser.add_argument('watermarked', type=inputs.boolean, help="Watermarked (Boolean)")

img_parser = parser.copy()
img_parser.add_argument('encoded_img', type=base64EncodedValueType, required=True, help='Base64 encoded version of the image to be decolourised.')
img_parser.remove_argument('encoded_img_url')

@api.route('/hello')
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

@api.route('/predict')
class Predict(Resource):

    # def __init__(self):
    #     super().__init__()    

    # @api.doc(description='Artistic Colourisation for an Image',
    #         body=input_predict)
    @api.expect(parser)
    @api.response(200,"success",output_predict)
    @api.response(400,"bad request",output_error)
    @api.response(500,"internal server error")
    def get(self):

        import tasks

        args = parser.parse_args()

        print(args)

        encoded_img_url = args.get('encoded_img_url',"")
        render_factor = args.get("render_factor",30)
        watermarked = args.get("watermarked",False)

        response = tasks.predictImgURL.delay(
            encoded_img_url,
            render_factor,
            watermarked
        ).get()

        # response = tasks.predictImg(
        #     encoded_img_url,
        #     render_factor,
        #     watermarked
        # )

        return response


    @api.expect(img_parser)
    @api.response(200,"success",output_predict)
    @api.response(400,"bad request",output_error)
    @api.response(500,"internal server error")
    def post(self):

        import tasks

        args = img_parser.parse_args()

        print(args)

        decoded_img_bytes = args.get('encoded_img',"")
        render_factor = args.get("render_factor",30)
        watermarked = args.get("watermarked",False)

        response = tasks.predictImg.delay(
            decoded_img_bytes,
            render_factor,
            watermarked
        ).get()

        # use the new method
        # response = tasks.JIT_predictImg.delay(
        #     decoded_img_bytes,
        #     render_factor,
        #     watermarked
        # ).get()


        return response


@api.route('/jitpredict')
class JITPredict(Resource):


    @api.expect(img_parser)
    @api.response(200,"success",output_predict)
    @api.response(400,"bad request",output_error)
    @api.response(500,"internal server error")
    def post(self):

        import tasks

        args = img_parser.parse_args()

        print(args)

        decoded_img_bytes = args.get('encoded_img',"")
        render_factor = args.get("render_factor",30)
        watermarked = args.get("watermarked",False)

        response = tasks.JIT_predictImg.delay(
            decoded_img_bytes,
            render_factor,
            watermarked
        ).get()

        return response

@api.route('/oldpredict')
class OldPredict(Resource):


    @api.expect(img_parser)
    @api.response(200,"success",output_predict)
    @api.response(400,"bad request",output_error)
    @api.response(500,"internal server error")
    def post(self):

        import tasks_archive

        args = img_parser.parse_args()

        print(args)

        decoded_img_bytes = args.get('encoded_img',"")
        render_factor = args.get("render_factor",30)
        watermarked = args.get("watermarked",False)

        response = tasks_archive.predictImg.delay(
            decoded_img_bytes,
            render_factor,
            watermarked
        ).get()

        return response
