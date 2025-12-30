import sys
import os

# Adiciona o caminho do projeto ao Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.database import db

class EstoqueService:
    def criar_item(self, descricao, quantidade, u_m, validade, valor_medio, tipo):
        conn = db.get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute(
                """INSERT INTO estoque (descricao, quantidade, u_m, validade, valor_medio) 
                   VALUES (?, ?, ?, ?, ?)""",
                (descricao, quantidade, u_m, validade, valor_medio)
            )
            id_item = cursor.lastrowid
            
            cursor.execute(
                "INSERT INTO categoria (ID_item, tipo) VALUES (?, ?)",
                (id_item, tipo)
            )
            
            conn.commit()
            return {"id": id_item, "message": "Item criado com sucesso"}
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()
    
    def listar_estoque(self):
        conn = db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.*, c.tipo 
                FROM estoque e 
                LEFT JOIN categoria c ON e.ID = c.ID_item
            """)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()

estoque_service = EstoqueService()