# 🚀 IAN Backend API

Backend para Intelligent Analytics Network - Plataforma de Trading con IA.

## 📡 Endpoints Disponibles

| Endpoint | Descripción |
|----------|-------------|
| `GET /` | Información del API |
| `GET /health` | Health check |
| `GET /stock/{symbol}` | Datos actuales de una acción |
| `GET /stock/{symbol}/history?period=1mo` | Historial de precios |
| `GET /market/summary` | Resumen de índices del mercado |
| `GET /stocks/batch?symbols=AAPL,MSFT` | Múltiples acciones a la vez |

## 🛠️ Tecnologías

- **FastAPI** - Framework web
- **yfinance** - Datos de Yahoo Finance
- **Uvicorn** - Servidor ASGI

## 🚀 Deploy en Railway

1. Crea cuenta en [railway.app](https://railway.app)
2. Conecta tu GitHub
3. Crea nuevo proyecto → Deploy from GitHub repo
4. Selecciona este repositorio
5. Railway detectará automáticamente Python y desplegará

## 💻 Desarrollo Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Correr servidor
python main.py

# O con uvicorn
uvicorn main:app --reload
```

El API estará en `http://localhost:8000`

## 📝 Ejemplos de Uso

```bash
# Obtener datos de Apple
curl https://tu-api.railway.app/stock/AAPL

# Historial de 3 meses
curl https://tu-api.railway.app/stock/TSLA/history?period=3mo

# Múltiples acciones
curl https://tu-api.railway.app/stocks/batch?symbols=AAPL,MSFT,NVDA
```

## ⚠️ Notas

- Los datos provienen de Yahoo Finance (gratuito)
- Hay límites de rate en Yahoo Finance
- Para uso intensivo, considera APIs premium

---

Parte del proyecto **IAN - Intelligent Analytics Network**
