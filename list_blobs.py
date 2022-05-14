from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

from FlaskServer.app_database import FileStorage

from tabulate import tabulate
import pandas as pd

file_storage = FileStorage()

imgs = file_storage.list_imgs()

df = pd.DataFrame(imgs).sort_values(by="Blob Creation Dates")

print(df)