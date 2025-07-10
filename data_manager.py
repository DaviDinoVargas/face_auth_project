# data_manager.py
import json
import os
from pathlib import Path
import re

class DataManager:
    def __init__(self):
        self.users_data = []
        self.data_dir = Path("A:/python/face_auth_project/faces")
        self._ensure_data_dir_exists()
        self.load_users()

    def _ensure_data_dir_exists(self):
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Erro ao criar diretório: {e}")

    def _get_next_id(self):
        existing_files = list(self.data_dir.glob("*.json"))
        if not existing_files:
            return 1
        ids = []
        for file in existing_files:
            match = re.search(r'_id_(\d+)\.json$', file.name)
            if match:
                ids.append(int(match.group(1)))
        return max(ids) + 1 if ids else 1

    def load_users(self):
        self.users_data = []
        for file in self.data_dir.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Verifica se o arquivo tem a estrutura correta
                    if all(key in data for key in ['username', 'id', 'landmarks']):
                        data['filename'] = file.name
                        self.users_data.append(data)
                    else:
                        print(f"Arquivo ignorado (formato inválido): {file.name}")
            except Exception as e:
                print(f"Erro ao carregar {file}: {e}")

    def add_user(self, username, landmarks):
    # Verificação extra de landmarks vazias
        if not landmarks or len(landmarks) != 5:
            raise ValueError("Dados faciais inválidos para cadastro")
        # Verifica se o username já existe
        if any(user['username'] == username for user in self.users_data):
            raise ValueError("Usuário já existe!")
    
        # Gera novo ID
        user_id = self._get_next_id()
        filename = f"{username}_id_{user_id:06d}.json"
        
        # Cria estrutura de dados
        user_data = {
            "username": username,
            "id": user_id,
            "landmarks": landmarks,
            "filename": filename
        }
        
        # Salva em arquivo
        try:
            with open(self.data_dir / filename, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, indent=4, ensure_ascii=False)
            self.load_users()  # Recarrega a lista
        except Exception as e:
            print(f"Erro ao salvar: {e}")
            raise

    def delete_user(self, filename):
        try:
            (self.data_dir / filename).unlink()
            self.load_users()  # Atualiza a lista após remover
        except Exception as e:
            print(f"Erro ao excluir usuário: {e}")

    def get_user_landmarks(self, username):
        for user in self.users_data:
            if user['username'] == username:
                return user['landmarks']
        return None
    
    def get_users_safe(self):
        return [u for u in self.users_data if 'username' in u and 'id' in u]
