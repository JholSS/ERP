import sqlite3
import os

class Database:
    def __init__(self):
        self.database_path = "../../shared/erp.db"  
        self.criar_tabelas()
    
    def get_connection(self):
        """Retorna conexão com o banco"""
        os.makedirs("../../shared", exist_ok=True) 
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

# Instância global do banco
db = Database()