import os
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
from django.conf import settings


logger = logging.getLogger(__name__)

class DriveService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            try:
                cls._instance._initialize()
            except Exception as e:
                logger.error(f"Falha na inicialização do DriveService: {str(e)}")
                raise
        return cls._instance

    def _initialize(self):
        SCOPES = ['https://www.googleapis.com/auth/drive']
        SERVICE_ACCOUNT_FILE = os.path.join(settings.BASE_DIR, "credentials.json")

        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            raise Exception("Arquivo credentials.json (service account) não encontrado")

        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )

        self.service = build('drive', 'v3', credentials=creds)
        logger.info("Serviço do Drive inicializado com sucesso (service account).")

    def test_folder_access(self, folder_id: str) -> bool:
        """Verifica se a pasta existe (Meu Drive ou Shared Drive)."""
        try:
            result = self.service.files().get(
                fileId=folder_id,
                fields='id,name',
                supportsAllDrives=True
            ).execute()

            logger.info(f"Acesso confirmado à pasta: {result['name']} (ID: {result['id']})")
            return True
        except HttpError as e:
            logger.error(f"Erro HTTP ao acessar pasta: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro geral ao acessar pasta: {e}")
            return False

    def find_or_create_folder(self, folder_name: str, parent_folder_id: str = None) -> str:
        """Procura por uma pasta com o nome especificado e cria se não existir."""
        try:
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            if parent_folder_id:
                query += f" and '{parent_folder_id}' in parents"

            results = self.service.files().list(
                q=query,
                fields='files(id, name)',
                includeItemsFromAllDrives=True,
                supportsAllDrives=True
            ).execute()

            folders = results.get('files', [])
            if folders:
                return folders[0]['id']

            return self.create_folder(folder_name, parent_folder_id)
        except Exception as e:
            logger.error(f"Erro em find_or_create_folder: {str(e)}")
            raise

    def create_folder(self, folder_name: str, parent_folder_id: str = None) -> str:
        """Cria uma pasta dentro do Meu Drive ou Shared Drive."""
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]

        try:
            folder = self.service.files().create(
                body=file_metadata,
                fields='id',
                supportsAllDrives=True
            ).execute()
            logger.info(f"Pasta criada: {folder_name} (ID: {folder['id']})")
            return folder.get('id')
        except Exception as e:
            logger.error(f"Erro ao criar pasta: {str(e)}")
            raise

    def upload_file(self, file_name: str, file_content: bytes, mime_type: str, folder_id: str = None) -> str:
        """Faz upload de um arquivo para Meu Drive ou Shared Drive."""
        file_metadata = {'name': file_name}
        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaIoBaseUpload(
            BytesIO(file_content),
            mimetype=mime_type,
            resumable=True
        )

        try:
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id',
                supportsAllDrives=True
            ).execute()
            logger.info(f"Arquivo {file_name} enviado com sucesso (ID: {file['id']})")
            return file.get('id')
        except Exception as e:
            logger.error(f"Erro ao fazer upload: {str(e)}")
            raise
