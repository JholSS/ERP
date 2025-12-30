import sys
import os

# Adiciona o caminho do projeto ao Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.database import db

class FolhaService:
    def criar_registro(self, id_usuario, salario, descontos, mes_ref):
        conn = db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO folhapag (ID_usuario, salario, descontos, mesRef) 
                   VALUES (?, ?, ?, ?)""",
                (id_usuario, salario, descontos, mes_ref)
            )
            conn.commit()
            return {"id": cursor.lastrowid, "message": "Registro criado com sucesso"}
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()
    
    def listar_folha(self):
        conn = db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT f.*, u.Nome as usuario_nome 
                FROM folhapag f 
                LEFT JOIN usuario u ON f.ID_usuario = u.ID
            """)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()

folha_service = FolhaService()