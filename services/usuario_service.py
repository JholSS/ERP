import sys
import os

# Adiciona o caminho do projeto ao Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.database import db  # ⬅️ AGORA VAI FUNCIONAR!

class UsuarioService:
    def criar_usuario(self, nome, email, funcao):
        conn = db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuario (Nome, Email, Funcao) VALUES (?, ?, ?)",
                (nome, email, funcao)
            )
            conn.commit()
            return {"id": cursor.lastrowid, "message": "Usuário criado com sucesso"}
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()
    
    def listar_usuarios(self):
        conn = db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuario")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()

usuario_service = UsuarioService()