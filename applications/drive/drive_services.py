import json
import logging
from io import BytesIO
from typing import Optional, Dict, Any

from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload

logger = logging.getLogger(__name__)


class DriveServiceInitError(Exception):
    """Erro de inicialização do DriveService (credenciais, chave, escopos, etc.)."""
    pass


class DriveService:
    _instance: Optional["DriveService"] = None
    service = None  # evita AttributeError caso a init falhe

    def __new__(cls):
        if cls._instance is None:
            inst = super().__new__(cls)
            try:
                inst._initialize()
            except Exception as e:
                logger.error(f"Falha na inicialização do DriveService: {e}")
                # não mantém instância quebrada em cache
                raise
            cls._instance = inst
        return cls._instance

    def _initialize(self) -> None:
        SCOPES = ['https://www.googleapis.com/auth/drive']

        raw = getattr(settings, "GOOGLE_CREDENTIALS_JSON", None)
        if raw is None:
            raise DriveServiceInitError("GOOGLE_CREDENTIALS_JSON ausente nos settings.")

        # Aceita dict (local) ou string JSON (produção via ENV)
        if isinstance(raw, str):
            try:
                info = json.loads(raw)
            except Exception as e:
                raise DriveServiceInitError("GOOGLE_CREDENTIALS_JSON inválido (string JSON malformada).") from e
        elif isinstance(raw, dict):
            info = dict(raw)  # cópia defensiva
        else:
            raise DriveServiceInitError(f"Tipo inválido para GOOGLE_CREDENTIALS_JSON: {type(raw).__name__}")

        # Valida chaves mínimas
        required = {"type", "project_id", "private_key_id", "private_key", "client_email", "client_id", "token_uri"}
        missing = required - info.keys()
        if missing:
            raise DriveServiceInitError(f"Credenciais faltando chaves: {', '.join(sorted(missing))}")

        # Normaliza a private_key (caso venha com '\\n' ou CRLF)
        pk = info.get("private_key")
        if not isinstance(pk, str) or not pk:
            raise DriveServiceInitError("private_key ausente ou vazia.")
        # substitui literais '\\n' por quebra real e normaliza finais de linha
        pk_norm = pk.replace("\\n", "\n").replace("\r\n", "\n").strip()

        # Checagens rápidas de formato
        if not pk_norm.startswith("-----BEGIN PRIVATE KEY-----") or not pk_norm.endswith("-----END PRIVATE KEY-----"):
            raise DriveServiceInitError(
                "private_key não contém cabeçalho/rodapé válidos "
                "(esperado BEGIN/END PRIVATE KEY). Verifique as quebras de linha."
            )

        info["private_key"] = pk_norm

        # Cria credenciais e client
        try:
            creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("Serviço do Drive inicializado com sucesso (GOOGLE_CREDENTIALS_JSON).")
        except Exception as e:
            # Erros comuns aqui: chave corrompida, newline errado, projeto/SA sem Drive API
            raise DriveServiceInitError(
                "Falha ao construir credenciais do Google Drive. "
                "Geralmente é private_key inválida ou com quebras de linha incorretas."
            ) from e

    # ------------ utilitários ------------

    def test_folder_access(self, folder_id: str) -> bool:
        try:
            result = self.service.files().get(
                fileId=folder_id, fields='id,name', supportsAllDrives=True
            ).execute()
            logger.info(f"Acesso confirmado à pasta: {result['name']} (ID: {result['id']})")
            return True
        except HttpError as e:
            logger.error(f"Erro HTTP ao acessar pasta: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro geral ao acessar pasta: {e}")
            return False

    def find_or_create_folder(self, folder_name: str, parent_folder_id: Optional[str] = None) -> str:
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
            logger.error(f"Erro em find_or_create_folder: {e}")
            raise

    def create_folder(self, folder_name: str, parent_folder_id: Optional[str] = None) -> str:
        metadata: Dict[str, Any] = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
        if parent_folder_id:
            metadata['parents'] = [parent_folder_id]

        try:
            folder = self.service.files().create(
                body=metadata, fields='id', supportsAllDrives=True
            ).execute()
            logger.info(f"Pasta criada: {folder_name} (ID: {folder['id']})")
            return folder['id']
        except Exception as e:
            logger.error(f"Erro ao criar pasta: {e}")
            raise

    def upload_file(self, file_name: str, file_content: bytes, mime_type: str, folder_id: Optional[str] = None) -> str:
        metadata: Dict[str, Any] = {'name': file_name}
        if folder_id:
            metadata['parents'] = [folder_id]

        media = MediaIoBaseUpload(BytesIO(file_content), mimetype=mime_type, resumable=True)

        try:
            file = self.service.files().create(
                body=metadata, media_body=media, fields='id', supportsAllDrives=True
            ).execute()
            logger.info(f"Arquivo {file_name} enviado com sucesso (ID: {file['id']})")
            return file['id']
        except Exception as e:
            logger.error(f"Erro ao fazer upload: {e}")
            raise
    
    def delete_file(self, file_id: str) -> bool:
        try:
            self.service.files().update(
                fileId=file_id,
                body={'trashed': True},
                supportsAllDrives=True
            ).execute()
            logger.info(f"Arquivo {file_id} movido para lixeira com sucesso.")
            return True
        except HttpError as e:
            logger.error(f"Erro ao mover arquivo {file_id} para lixeira: {e}")
            return False
        
    # def delete_file_permanetly(self, file_id):
    #     try:
    #         self.service.files().delete(fileId=file_id).execute()
    #         print(f"Arquivo {file_id} removido com sucesso do Drive.")
    #         return True
    #     except HttpError as e:
    #         print(f"Erro ao remover arquivo {file_id}: {e}")
    #         return False