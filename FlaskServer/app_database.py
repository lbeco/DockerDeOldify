import os, uuid

# from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import boto3
from PIL import Image
import io

class AWSS2Database:
    def __init__(self, container_name):
        # self.s3 = boto3.resource('s3').Bucket('bucketfordeoldify')
        self.s3_client = boto3.client('s3')
        self.container_name = container_name

        # Create the BlobServiceClient object which will be used to create a container client
        # self.blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        # self.container_name = container_name

    def upload_blob(self, input_bytes: bytes, blob_name: str):
        # blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)

        self.s3_client.put_object(Bucket=self.container_name,Key=blob_name,Body=input_bytes,ACL='public-read')

        return "https://bucketfordeoldify.s3.amazonaws.com/" + blob_name
        

    def list_blobs(self):

        container_client = self.blob_service_client.get_container_client(self.container_name)
        blobs_list = container_client.list_blobs()

        return blobs_list


class FileStorage(AWSS2Database):
    def __init__(self):
        container_name = self.generate_azure_blob_storage_config()
        super().__init__(container_name)

    @staticmethod
    def generate_azure_blob_storage_config():

        # Create a unique name for the container
        container_name = 'bucketfordeoldify'

        return container_name

    def upload_img(self, img, blob_name):

        output_img_byte_arr = io.BytesIO()

        # Convert composite to RGB so we can save as JPEG
        img.save(output_img_byte_arr, format='JPEG')

        return self.upload_blob(output_img_byte_arr.getvalue(), blob_name)    

    def list_imgs(self):

        blobs_list = self.list_blobs()

        output_dict = {}

        for blob in blobs_list:
            output_dict["Blob Names"] = output_dict.get("Blob Names",[]) + [blob.name]
            output_dict["Blob Creation Dates"] = output_dict.get("Blob Creation Dates",[]) + [blob.creation_time]
            output_dict["Blob Size"] = output_dict.get("Blob Size",[]) + [blob.size]     
            output_dict["Blob URL"] = output_dict.get("Blob URL",[]) + [blob.url]

        return output_dict


if __name__ == "__main__":
    # connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    bucket_name = 'bucketfordeoldify'
