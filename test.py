from azure.storage.blob import BlobServiceClient
import yaml


def upload_blob(connection_string, container_name, local_file_path, blob_name):
  try:
    blob_service_client = BlobServiceClient.from_connection_string(conn_str=connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    
    with open(local_file_path, "rb") as data:
      blob_client.upload_blob(data, overwrite=True)

    print(f"File '{local_file_path}' uploaded to blob '{blob_name}' successfully.")

  except Exception as e:
    print(f"Error uploading file: {e}")
    raise




with open('Config.yaml','r') as f:
    config = yaml.load(f,Loader=yaml.SafeLoader)

connection_string = config['blob']['Connection_string']
container_name = "profilepics"
local_file_path = "./pro-2.jpg"
blob_name = "pro2.jpg"

upload_blob(connection_string, container_name, local_file_path, blob_name)