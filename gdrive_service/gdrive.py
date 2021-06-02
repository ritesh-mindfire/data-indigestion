from __future__ import print_function

import os.path
import io

from datetime import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from apiclient.http import MediaIoBaseDownload, MediaFileUpload
# https://developers.google.com/analytics/devguides/config/mgmt/v3/quickstart/service-py
# from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from django.conf import settings

import logging
logger = logging.getLogger('quickstart')

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']
credentials_file_path = os.path.join(settings.BASE_DIR, 'gdrive_service', 'sa-credentials.json')
# credentials_file_path = 'credentials.json'


class GDriveService:
    """
    """
    def __init__(self, media_downloadpath):
        creds = self.get_sa_credentials()
        self.media_downloadpath = media_downloadpath
        self.drive_service = build('drive', 'v3', credentials=creds)
    
    def get_sa_credentials(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_file_path, scopes=SCOPES)
        return credentials
    
    def get_credentials(self, token_file_path):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(token_file_path):
            creds = Credentials.from_authorized_user_file(token_file_path, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                import pdb; pdb.set_trace()
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file_path, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_file_path, 'w') as token:
                token.write(creds.to_json())

        return creds

    def download_drive_file(self, file_id, file_name):
        folder_path = self.media_downloadpath
        if not os.path.isdir(folder_path):
            os.mkdir(folder_path)
        
        request = self.drive_service.files().get_media(fileId=file_id)
        file_path = os.path.join(folder_path, file_name)
        fh = io.FileIO(file_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))

    def fetch_drive_folder_files(self, folder_id):
        page_token = None
        while True:
            response = self.drive_service.files().list(q="'{}' in parents and createdTime > '{}T5:00:00'".format(
                                                folder_id, datetime.strftime(datetime.now(), '%Y-%m-%d')),
                                                spaces='drive',
                                                fields='nextPageToken, files(id, name)',
                                                pageToken=page_token).execute()
            if not response.get('files'):
                logger.info('No File is available on Drive to download for today.')
                break

            for file in response.get('files', []):
                # Process change
                print('Found file: %s (%s)' % (file.get('name'), file.get('id')))
                self.download_drive_file(file.get('id'), file.get('name'))

            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

    def fetch_drive_folders(self, folder_name):
        page_token = None
        folder_id = None
        while True:
            response = self.drive_service.files().list(q="mimeType='application/vnd.google-apps.folder' and trashed=false",
                                                spaces='drive',
                                                fields='nextPageToken, files(id, name)',
                                                pageToken=page_token).execute()
            for file in response.get('files', []):
                print('Found Folder: %s (%s)' % (file.get('name'), file.get('id')))
                if file.get('name') == folder_name:
                    folder_id = file.get('id')
                    break

            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
            if folder_id:
                break

        return folder_id    
    
    ## create folder in gdrive - Report    
    def create_drive_folder(self, folder_name):
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        file = self.drive_service.files().create(body=file_metadata,
                                            fields='id,name,').execute()
        print('Folder created ID: %s (%s)' % (file.get('name'), file.get('id')))
        return file.get('id')
       
    # upload report file in gdrive folder
    def upload_drive_files(self, folder_id, file_path):
        file_name = file_path.split('/')[-1]
        file_metadata = {'name': file_name, 'parents': [folder_id]}
        media = MediaFileUpload(file_path)
        file = self.drive_service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id,name,mimeType').execute()
        print('File Upload: %s (%s) %s' % (file.get('name'), file.get('id'), file.get('mimeType')))


if __name__ == '__main__':
    gdrive_instance = GDriveService('../media_download')

    # folder_id = gdrive_instance.fetch_drive_folders('Manufacture Data')
    # if folder_id:
    #     gdrive_instance.fetch_drive_folder_files(folder_id)
    # else:
    #     print("Folder name does not exist with name Manufacture Data")
    
    folder_id = gdrive_instance.fetch_drive_folders('Report')
    if not folder_id:
        folder_id = gdrive_instance.create_drive_folder('Report')

    # file_path = 'sample.py'
    # gdrive_instance.upload_drive_files(folder_id, file_path)

