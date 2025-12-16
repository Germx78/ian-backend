from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import requests

app = FastAPI(
    title="IAN Backend API",
    description="Backend para Intelligent Analytics Network - Plataforma de Trading",
    version="1.0.0"
)

# Configuración CORS simple y funcional
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Headers para simular navegador
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
}

# ==================== FUNCIONES HELPER ====================

def get_yahoo_quote(symbol: str):
    """Obtener cotización usando Yahoo Finance API directa"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {
        'interval': '1d',
        'range': '1d'
    }
    
    response = requests.get(url, headers=HEADERS, params=params, timeout=10)
    
    if response.status_code != 200:
        raise Exception(f"Yahoo Finance respondió con status {response.status_code}")
    
    data = response.json()
    
    if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
        raise Exception("No se encontraron datos para este símbolo")
    
    result = data['chart']['result'][0]
    meta = result['meta']
    
    current_price = meta.get('regularMarketPrice', 0)
    previous_close = meta.get('chartPreviousClose', meta.get('previousClose', 0))
    
    return {
        "symbol": symbol.upper(),
        "name": meta.get('shortName', meta.get('longName', symbol)),
        "price": round(current_price, 2),
        "previousClose": round(previous_close, 2),
        "change": round(current_price - previous_close, 2),
        "changePercent": round(((current_price - previous_close) / previous_close * 100) if previous_close else 0, 2),
        "dayHigh": round(meta.get('regularMarketDayHigh', 0), 2),
        "dayLow": round(meta.get('regularMarketDayLow', 0), 2),
        "volume": meta.get('regularMarketVolume', 0),
        "marketCap": meta.get('marketCap', 0),
        "exchange": meta.get('exchangeName', 'N/A'),
        "currency": meta.get('currency', 'USD'),
        "timestamp": datetime.now().isoformat()
    }


def get_yahoo_history(symbol: str, period: str = "1mo"):
    """Obtener historial de precios"""
    range_map = {
        "1d": "1d",
        "5d": "5d", 
        "1mo": "1mo",
        "3mo": "3mo",
        "6mo": "6mo",
        "1y": "1y",
        "2y": "2y",
        "5y": "5y",
        "max": "max"
    }
    
    yahoo_range = range_map.get(period, "1mo")
    
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {
        'interval': '1d',
        'range': yahoo_range
    }
    
    response = requests.get(url, headers=HEADERS, params=params, timeout=10)
    
    if response.status_code != 200:
        raise Exception(f"Yahoo Finance respondió con status {response.status_code}")
    
    data = response.json()
    
    if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
        raise Exception("No se encontraron datos para este símbolo")
    
    result = data['chart']['result'][0]
    timestamps = result.get('timestamp', [])
    quotes = result.get('indicators', {}).get('quote', [{}])[0]
    
    history = []
    for i, ts in enumerate(timestamps):
        if quotes.get('close') and len(quotes['close']) > i and quotes['close'][i] is not None:
            history.append({
                "date": datetime.fromtimestamp(ts).strftime("%Y-%m-%d"),
                "open": round(quotes.get('open', [0])[i] or 0, 2),
                "high": round(quotes.get('high', [0])[i] or 0, 2),
                "low": round(quotes.get('low', [0])[i] or 0, 2),
                "close": round(quotes.get('close', [0])[i] or 0, 2),
                "volume": int(quotes.get('volume', [0])[i] or 0)
            })
    
    return history


# ==================== ENDPOINTS ====================

@app.get("/")
def root():
    """Endpoint de bienvenida"""
    return {
        "message": "🚀 IAN Backend API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": [
            "/stock/{symbol}",
            "/stock/{symbol}/history",
            "/market/summary",
            "/stocks/batch",
            "/health"
        ]
    }


@app.get("/health")
def health_check():
    """Verificar que el servidor está funcionando"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/test")
def test_endpoint():
    """Endpoint de prueba con datos estáticos para verificar CORS"""
    return {
        "timestamp": datetime.now().isoformat(),
        "count": 3,
        "stocks": [
            {"symbol": "AAPL", "name": "Apple Inc.", "price": 185.50, "change": 2.30, "changePercent": 1.25},
            {"symbol": "MSFT", "name": "Microsoft", "price": 378.20, "change": -1.50, "changePercent": -0.40},
            {"symbol": "NVDA", "name": "NVIDIA", "price": 456.80, "change": 5.20, "changePercent": 1.15}
        ]
    }


@app.get("/stock/{symbol}")
def get_stock_data(symbol: str):
    """
    Obtener datos actuales de una acción
    Ejemplo: /stock/AAPL
    """
    try:
        return get_yahoo_quote(symbol.upper())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error obteniendo datos de {symbol}: {str(e)}")


@app.get("/stock/{symbol}/history")
def get_stock_history(symbol: str, period: str = "1mo"):
    """
    Obtener historial de precios
    Períodos: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max
    """
    valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
    
    if period not in valid_periods:
        raise HTTPException(status_code=400, detail=f"Período inválido. Usa: {valid_periods}")
    
    try:
        history = get_yahoo_history(symbol.upper(), period)
        return {
            "symbol": symbol.upper(),
            "period": period,
            "count": len(history),
            "data": history
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error obteniendo historial de {symbol}: {str(e)}")


@app.get("/market/summary")
def get_market_summary():
    """Obtener resumen de índices principales"""
    indices = ["SPY", "QQQ", "DIA", "IWM"]
    summary = []
    
    for symbol in indices:
        try:
            data = get_yahoo_quote(symbol)
            summary.append({
                "symbol": symbol,
                "name": data["name"],
                "price": data["price"],
                "change": data["change"],
                "changePercent": data["changePercent"]
            })
        except:
            summary.append({
                "symbol": symbol,
                "error": True
            })
    
    return {
        "timestamp": datetime.now().isoformat(),
        "indices": summary
    }


@app.get("/stocks/batch")
def get_batch_stocks(symbols: str = "AAPL,MSFT,GOOGL,NVDA,TSLA"):
    """
    Obtener datos de múltiples acciones
    Ejemplo: /stocks/batch?symbols=AAPL,MSFT,GOOGL
    """
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    
    if len(symbol_list) > 20:
        raise HTTPException(status_code=400, detail="Máximo 20 símbolos por solicitud")
    
    results = []
    
    for symbol in symbol_list:
        try:
            data = get_yahoo_quote(symbol)
            results.append(data)
        except:
            results.append({
                "symbol": symbol,
                "error": True
            })
    
    return {
        "timestamp": datetime.now().isoformat(),
        "count": len(results),
        "stocks": results
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
