import os
import ftplib
from dotenv import load_dotenv

load_dotenv()

class FTPManager:
    """
    Gestionnaire FTP pour rendre les kits de bienvenue persistants.
    """
    def __init__(self):
        self.host = os.getenv("FTP_HOST")
        self.user = os.getenv("FTP_USER")
        self.password = os.getenv("FTP_PASS")
        self.base_path = os.getenv("FTP_BASE_PATH", "/public_html/welcome")

    def upload_directory(self, local_dir, remote_subdir):
        """
        Upload récursif d'un dossier local vers le serveur FTP.
        """
        try:
            ftp = ftplib.FTP(self.host)
            ftp.login(self.user, self.password)
            
            # Naviguer ou créer le chemin de base
            self._ensure_dir(ftp, self.base_path)
            
            # Créer le sous-dossier spécifique au kit
            target_path = f"{self.base_path}/{remote_subdir}"
            self._ensure_dir(ftp, target_path)
            
            # Uploader les fichiers
            for root, dirs, files in os.walk(local_dir):
                for fname in files:
                    local_path = os.path.join(root, fname)
                    # Calculer le chemin relatif pour le FTP
                    rel_path = os.path.relpath(local_path, local_dir)
                    # Créer les sous-dossiers si nécessaire sur le FTP
                    remote_file_path = f"{target_path}/{rel_path}"
                    
                    # On s'assure que le dossier parent existe sur le FTP
                    remote_dir = os.path.dirname(remote_file_path)
                    self._ensure_dir(ftp, remote_dir)
                    
                    with open(local_path, "rb") as f:
                        print(f"⬆️ FTP Uploading: {rel_path}")
                        ftp.storbinary(f"STOR {remote_file_path}", f)
            
            ftp.quit()
            return True
        except Exception as e:
            print(f"❌ FTP Error: {e}")
            return False

    def _ensure_dir(self, ftp, path):
        """
        Vérifie si un dossier existe, sinon le crée (gère les chemins profonds).
        """
        parts = path.strip("/").split("/")
        current_path = ""
        for part in parts:
            current_path += "/" + part
            try:
                ftp.cwd(current_path)
            except:
                try:
                    ftp.mkd(current_path)
                    ftp.cwd(current_path)
                except Exception as e:
                    # Le dossier existe peut-être déjà ou erreur de droits
                    pass

if __name__ == "__main__":
    # Test simple
    manager = FTPManager()
    # manager.upload_directory("./dist/Test", "test_run")
