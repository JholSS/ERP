import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from services.usuario_service import usuario_service
    print("✅ usuario_service importado!")
except ImportError as e:
    print(f"❌ usuario_service erro: {e}")

try:
    from services.estoque_service import estoque_service
    print("✅ estoque_service importado!")
except ImportError as e:
    print(f"❌ estoque_service erro: {e}")

try:
    from services.folha_service import folha_service
    print("✅ folha_service importado!")
except ImportError as e:
    print(f"❌ folha_service erro: {e}")

try:
    from database.database import db
    print("✅ database importado!")
except ImportError as e:
    print(f"❌ database erro: {e}")