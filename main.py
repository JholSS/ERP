from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlite3
import os
import uvicorn
from datetime import date

app = FastAPI(title="ERP API", version="1.0.0")

# ========== CONFIGURAÇÃO DO BANCO ==========
def get_db_connection():
    """Conexão com o banco SQLite"""
    # CORRIGIDO: Criar pasta shared no diretório correto
    base_dir = os.path.dirname(os.path.abspath(__file__))
    shared_dir = os.path.join(base_dir, "..", "shared")
    os.makedirs(shared_dir, exist_ok=True)
    
    db_path = os.path.join(shared_dir, "erp.db")
    print(f"📁 Banco de dados: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def criar_tabelas():
    """Cria todas as tabelas do sistema"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    #Tabela usuario
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome TEXT NOT NULL,
            Email TEXT NOT NULL,
            Funcao TEXT NOT NULL,
            Data_admissao DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    #Tabela estoque
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estoque (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            u_m TEXT NOT NULL,
            entrada DATETIME DEFAULT CURRENT_TIMESTAMP,
            validade DATE NOT NULL,
            valor_medio REAL NOT NULL
        )
    ''')
    
    #Tabela categoria
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categoria (
            ID_item INTEGER NOT NULL,
            tipo TEXT,
            PRIMARY KEY (ID_item)
        )
    ''')

    # Tabela folhapag
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS folhapag (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_usuario INTEGER NOT NULL,
            salario REAL,
            descontos REAL,
            mesRef DATE
        )
    ''')
    
    # Tabela ferias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ferias (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_usuario INTEGER NOT NULL,
            inicio_ferias DATE,
            termino_ferias DATE,
            status TEXT
        )
    ''')

    #Tabela fiscal
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fiscal (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL,
        valor REAL NOT NULL,
        data_emissao DATE NOT NULL,
        tipo TEXT NOT NULL
        )
    ''')

    #Tabela financeiro
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS financeiro (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL,
        valor REAL NOT NULL,
        data DATE NOT NULL,
        categoria TEXT NOT NULL,
        tipo TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Tabelas criadas/verificadas com sucesso!")

# ========== MODELS ==========
class UsuarioCreate(BaseModel):
    Nome: str
    Email: str
    Funcao: str

class EstoqueCreate(BaseModel):
    descricao: str
    quantidade: int
    u_m: str
    validade: date
    valor_medio: float
    tipo: str

class FolhaCreate(BaseModel):
    ID_usuario: int
    salario: float
    descontos: float
    mesRef: date

class FeriasCreate(BaseModel):
    ID_usuario: int
    inicio_ferias: date
    termino_ferias: date
    status: str

class FiscalCreate(BaseModel):
    descricao: str
    valor: float
    data_emissao: date
    tipo: str  # 'ENTRADA' ou 'SAIDA'

class FinanceiroCreate(BaseModel):
    descricao: str
    valor: float
    data: date
    categoria: str
    tipo: str  # 'RECEITA' ou 'DESPESA'

class FinanceiroUpdate(BaseModel):
    descricao: str = None
    valor: float = None
    data: date = None
    categoria: str = None
    tipo: str = None

# ========== ROTAS ==========
@app.get("/")
def home():
    return {"message": "ERP API está funcionando!", "status": "online"}

#ROTAS USUÁRIO
@app.post("/usuarios/")
def criar_usuario(usuario: UsuarioCreate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuario (Nome, Email, Funcao) VALUES (?, ?, ?)",
            (usuario.Nome, usuario.Email, usuario.Funcao)
        )
        conn.commit()
        return {"message": "Usuário criado com sucesso", "id": cursor.lastrowid}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

@app.get("/usuarios/")
def listar_usuarios():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuario")
        usuarios = [dict(row) for row in cursor.fetchall()]
        return usuarios
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

@app.get("/usuarios/select/")
def obter_usuarios_select():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ID, Nome FROM usuario ORDER BY Nome")
        usuarios = [{"ID": row[0], "Nome": row[1]} for row in cursor.fetchall()]
        return usuarios
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

#Deletar usuário
@app.delete("/usuarios/{usuario_id}")
def deletar_usuario(usuario_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuario WHERE ID = ?", (usuario_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            return {"message": f"Usuário {usuario_id} deletado com sucesso"}
        else:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ROTAS ESTOQUE
@app.post("/estoque/")
def criar_item_estoque(item: EstoqueCreate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO estoque (descricao, quantidade, u_m, validade, valor_medio) VALUES (?, ?, ?, ?, ?)",
            (item.descricao, item.quantidade, item.u_m, item.validade, item.valor_medio)
        )
        id_item = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO categoria (ID_item, tipo) VALUES (?, ?)",
            (id_item, item.tipo)
        )
        
        conn.commit()
        return {"message": "Item criado com sucesso", "id": id_item}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

@app.get("/estoque/")
def listar_estoque():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT e.*, c.tipo FROM estoque e LEFT JOIN categoria c ON e.ID = c.ID_item")
        itens = [dict(row) for row in cursor.fetchall()]
        return itens
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

#Deletar item do estoque
@app.delete("/estoque/{item_id}")
def deletar_item_estoque(item_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        #Deletar da categoria primeiro (devido à chave estrangeira)
        cursor.execute("DELETE FROM categoria WHERE ID_item = ?", (item_id,))
        #Deletar do estoque
        cursor.execute("DELETE FROM estoque WHERE ID = ?", (item_id,))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            return {"message": f"Item {item_id} deletado com sucesso"}
        else:
            raise HTTPException(status_code=404, detail="Item não encontrado")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

#ROTAS FÉRIAS
@app.post("/ferias/")
def criar_ferias(ferias: FeriasCreate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ferias (ID_usuario, inicio_ferias, termino_ferias, status) VALUES (?, ?, ?, ?)",
            (ferias.ID_usuario, ferias.inicio_ferias, ferias.termino_ferias, ferias.status)
        )
        conn.commit()
        return {"message": "Férias registradas com sucesso", "id": cursor.lastrowid}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

@app.get("/ferias/")
def listar_ferias():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT f.*, u.Nome as usuario_nome 
            FROM ferias f 
            LEFT JOIN usuario u ON f.ID_usuario = u.ID
            ORDER BY f.inicio_ferias DESC
        """)
        ferias = [dict(row) for row in cursor.fetchall()]
        return ferias
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

# Deletar férias
@app.delete("/ferias/{ferias_id}")
def deletar_ferias(ferias_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ferias WHERE ID = ?", (ferias_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            return {"message": f"Férias {ferias_id} deletadas com sucesso"}
        else:
            raise HTTPException(status_code=404, detail="Férias não encontradas")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

#ROTAS FISCAL
@app.post("/fiscal/")
def criar_registro_fiscal(fiscal: FiscalCreate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO fiscal (descricao, valor, data_emissao, tipo) VALUES (?, ?, ?, ?)",
            (fiscal.descricao, fiscal.valor, fiscal.data_emissao, fiscal.tipo)
        )
        conn.commit()
        return {"message": "Registro fiscal criado com sucesso", "id": cursor.lastrowid}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

@app.get("/fiscal/")
def listar_fiscal():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fiscal ORDER BY data_emissao DESC")
        registros = [dict(row) for row in cursor.fetchall()]
        return registros
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

@app.delete("/fiscal/{registro_id}")
def deletar_registro_fiscal(registro_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM fiscal WHERE ID = ?", (registro_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            return {"message": f"Registro fiscal {registro_id} deletado com sucesso"}
        else:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

#ROTAS FINANCEIRO
@app.post("/financeiro/")
def criar_registro_financeiro(financeiro: FinanceiroCreate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO financeiro (descricao, valor, data, categoria, tipo) VALUES (?, ?, ?, ?, ?)",
            (financeiro.descricao, financeiro.valor, financeiro.data, financeiro.categoria, financeiro.tipo)
        )
        conn.commit()
        return {"message": "Registro financeiro criado com sucesso", "id": cursor.lastrowid}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

@app.get("/financeiro/")
def listar_financeiro():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM financeiro ORDER BY data DESC")
        registros = [dict(row) for row in cursor.fetchall()]
        return registros
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

@app.get("/financeiro/resumo/")
def resumo_financeiro():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Total receitas
        cursor.execute("SELECT SUM(valor) as total FROM financeiro WHERE tipo = 'RECEITA'")
        total_receitas = cursor.fetchone()[0] or 0
        
        # Total despesas
        cursor.execute("SELECT SUM(valor) as total FROM financeiro WHERE tipo = 'DESPESA'")
        total_despesas = cursor.fetchone()[0] or 0
        
        # Saldo atual
        saldo = total_receitas - total_despesas
        
        # Últimos 30 dias
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN tipo = 'RECEITA' THEN valor ELSE 0 END) as receitas_30d,
                SUM(CASE WHEN tipo = 'DESPESA' THEN valor ELSE 0 END) as despesas_30d
            FROM financeiro 
            WHERE data >= date('now', '-30 days')
        """)
        ultimos_30d = cursor.fetchone()
        receitas_30d = ultimos_30d[0] or 0
        despesas_30d = ultimos_30d[1] or 0
        
        return {
            "total_receitas": float(total_receitas),
            "total_despesas": float(total_despesas),
            "saldo": float(saldo),
            "receitas_30d": float(receitas_30d),
            "despesas_30d": float(despesas_30d)
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

@app.get("/financeiro/categorias/")
def listar_categorias():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT categoria FROM financeiro ORDER BY categoria")
        categorias = [row[0] for row in cursor.fetchall()]
        return categorias
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

#Deletar registro financeiro
@app.delete("/financeiro/{registro_id}")
def deletar_registro_financeiro(registro_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM financeiro WHERE ID = ?", (registro_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            return {"message": f"Registro financeiro {registro_id} deletado com sucesso"}
        else:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

#ROTAS FOLHA DE PAGAMENTO
@app.post("/folha/")
def criar_folha(folha: FolhaCreate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO folhapag (ID_usuario, salario, descontos, mesRef) 
               VALUES (?, ?, ?, ?)""",
            (folha.ID_usuario, folha.salario, folha.descontos, folha.mesRef)
        )
        conn.commit()
        return {"message": "Registro de folha criado com sucesso", "id": cursor.lastrowid}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

@app.get("/folha/")
def listar_folha():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT f.*, u.Nome as usuario_nome 
            FROM folhapag f 
            LEFT JOIN usuario u ON f.ID_usuario = u.ID
            ORDER BY f.mesRef DESC
        """)
        registros = [dict(row) for row in cursor.fetchall()]
        return registros
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

# Deletar folha de pagamento
@app.delete("/folha/{folha_id}")
def deletar_folha(folha_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM folhapag WHERE ID = ?", (folha_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            return {"message": f"Registro de folha {folha_id} deletado com sucesso"}
        else:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ========== INICIALIZAÇÃO ==========
if __name__ == "__main__":
    print("🚀 Iniciando ERP API...")
    criar_tabelas()
    print("🌐 Servidor rodando em: http://localhost:8000")
    print("📚 Documentação: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)