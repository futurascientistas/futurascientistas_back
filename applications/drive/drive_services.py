import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
import logging

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
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        self.token_file = 'token.json'
        self.creds = None
        self.service = None
        
        # 1. Tentar carregar credenciais existentes
        if os.path.exists(self.token_file):
            try:
                self.creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
            except Exception as e:
                logger.warning(f"Erro ao carregar token: {e}")
                os.unlink(self.token_file)
                self.creds = None
        
        # 2. Se não tem credenciais válidas, fazer nova autenticação
        if not self.creds or not self.creds.valid:
            if not os.path.exists('client_secrets.json'):
                raise Exception("Arquivo client_secrets.json não encontrado")
                
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json',
                self.SCOPES
            )
            self.creds = flow.run_local_server(port=8080, open_browser=True)
            
            # Salvar novas credenciais
            with open(self.token_file, 'w') as token:
                token.write(self.creds.to_json())
        
        # 3. Criar serviço
        self.service = build('drive', 'v3', credentials=self.creds)
        logger.info("Serviço do Drive inicializado com sucesso")

    def test_folder_access(self, folder_id):
        if not hasattr(self, 'service') or not self.service:
            self._initialize()
            
        try:
            result = self.service.files().get(
                fileId=folder_id,
                fields='id,name,capabilities'
            ).execute()
            
            if not result.get('capabilities', {}).get('canEdit', False):
                logger.warning("Tem acesso, mas não pode editar")
                return False
                
            logger.info(f"Acesso confirmado à pasta: {result['name']}")
            return True
            
        except HttpError as e:
            logger.error(f"Erro HTTP ao acessar pasta: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro geral ao acessar pasta: {e}")
            return False

    def find_or_create_folder(self, folder_name, parent_folder_id=None):
        """Procura por uma pasta com o nome especificado e cria se não existir"""
        if not hasattr(self, 'service') or not self.service:
            self._initialize()
            
        try:
            # Primeiro tenta encontrar a pasta
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            if parent_folder_id:
                query += f" and '{parent_folder_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                fields='files(id, name)'
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                # Pasta já existe, retorna o ID
                return folders[0]['id']
            
            # Se não existe, cria a pasta
            return self.create_folder(folder_name, parent_folder_id)
            
        except Exception as e:
            logger.error(f"Erro em find_or_create_folder: {str(e)}")
            raise

    def create_folder(self, folder_name, parent_folder_id=None):
        if not hasattr(self, 'service') or not self.service:
            self._initialize()
            
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]

        try:
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            return folder.get('id')
        except Exception as e:
            logger.error(f"Erro ao criar pasta: {str(e)}")
            raise

    def upload_file(self, file_name, file_content, mime_type, folder_id=None):
        from io import BytesIO
        from googleapiclient.http import MediaIoBaseUpload

        if not hasattr(self, 'service') or not self.service:
            self._initialize()

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
                fields='id'
            ).execute()
            return file.get('id')
        except Exception as e:
            logger.error(f"Erro ao fazer upload: {str(e)}")
            raise