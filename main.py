from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
from datetime import datetime, timedelta
import json

app = FastAPI(
    title="IAN Backend API",
    description="Backend para Intelligent Analytics Network - Plataforma de Trading",
    version="1.0.0"
)

# Permitir conexiones desde el frontend (Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: ["https://ian-platform.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            "/health"
        ]
    }

@app.get("/health")
def health_check():
    """Verificar que el servidor está funcionando"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/stock/{symbol}")
def get_stock_data(symbol: str):
    """
    Obtener datos actuales de una acción
    Ejemplo: /stock/AAPL
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        
        # Obtener precio actual y datos básicos
        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
        previous_close = info.get('previousClose') or info.get('regularMarketPreviousClose') or 0
        
        change = current_price - previous_close if current_price and previous_close else 0
        change_percent = (change / previous_close * 100) if previous_close else 0
        
        return {
            "symbol": symbol.upper(),
            "name": info.get('shortName') or info.get('longName') or symbol,
            "price": round(current_price, 2),
            "previousClose": round(previous_close, 2),
            "change": round(change, 2),
            "changePercent": round(change_percent, 2),
            "dayHigh": round(info.get('dayHigh') or 0, 2),
            "dayLow": round(info.get('dayLow') or 0, 2),
            "volume": info.get('volume') or 0,
            "avgVolume": info.get('averageVolume') or 0,
            "marketCap": info.get('marketCap') or 0,
            "peRatio": round(info.get('trailingPE') or 0, 2),
            "eps": round(info.get('trailingEps') or 0, 2),
            "week52High": round(info.get('fiftyTwoWeekHigh') or 0, 2),
            "week52Low": round(info.get('fiftyTwoWeekLow') or 0, 2),
            "dividend": round(info.get('dividendYield') or 0, 4),
            "sector": info.get('sector') or "N/A",
            "industry": info.get('industry') or "N/A",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error obteniendo datos de {symbol}: {str(e)}")


@app.get("/stock/{symbol}/history")
def get_stock_history(symbol: str, period: str = "1mo"):
    """
    Obtener historial de precios de una acción
    Períodos válidos: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max
    Ejemplo: /stock/AAPL/history?period=3mo
    """
    valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
    
    if period not in valid_periods:
        raise HTTPException(status_code=400, detail=f"Período inválido. Usa: {valid_periods}")
    
    try:
        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period=period)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No hay datos históricos para {symbol}")
        
        # Convertir a formato JSON-friendly
        data = []
        for date, row in hist.iterrows():
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(row['Open'], 2),
                "high": round(row['High'], 2),
                "low": round(row['Low'], 2),
                "close": round(row['Close'], 2),
                "volume": int(row['Volume'])
            })
        
        return {
            "symbol": symbol.upper(),
            "period": period,
            "count": len(data),
            "data": data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error obteniendo historial de {symbol}: {str(e)}")


@app.get("/market/summary")
def get_market_summary():
    """
    Obtener resumen del mercado (índices principales)
    """
    indices = {
        "SPY": "S&P 500",
        "QQQ": "Nasdaq 100",
        "DIA": "Dow Jones",
        "IWM": "Russell 2000",
        "VIX": "Volatility Index"
    }
    
    summary = []
    
    for symbol, name in indices.items():
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            current = info.get('currentPrice') or info.get('regularMarketPrice') or 0
            prev_close = info.get('previousClose') or info.get('regularMarketPreviousClose') or 0
            change = current - prev_close if current and prev_close else 0
            change_pct = (change / prev_close * 100) if prev_close else 0
            
            summary.append({
                "symbol": symbol,
                "name": name,
                "price": round(current, 2),
                "change": round(change, 2),
                "changePercent": round(change_pct, 2)
            })
        except:
            summary.append({
                "symbol": symbol,
                "name": name,
                "price": 0,
                "change": 0,
                "changePercent": 0,
                "error": True
            })
    
    return {
        "timestamp": datetime.now().isoformat(),
        "indices": summary
    }


@app.get("/stocks/batch")
def get_batch_stocks(symbols: str = "AAPL,MSFT,GOOGL,NVDA,TSLA"):
    """
    Obtener datos de múltiples acciones a la vez
    Ejemplo: /stocks/batch?symbols=AAPL,MSFT,GOOGL
    """
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    
    if len(symbol_list) > 20:
        raise HTTPException(status_code=400, detail="Máximo 20 símbolos por solicitud")
    
    results = []
    
    for symbol in symbol_list:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            current = info.get('currentPrice') or info.get('regularMarketPrice') or 0
            prev_close = info.get('previousClose') or 0
            change = current - prev_close if current and prev_close else 0
            change_pct = (change / prev_close * 100) if prev_close else 0
            
            results.append({
                "symbol": symbol,
                "name": info.get('shortName') or symbol,
                "price": round(current, 2),
                "change": round(change, 2),
                "changePercent": round(change_pct, 2),
                "volume": info.get('volume') or 0
            })
        except:
            results.append({
                "symbol": symbol,
                "price": 0,
                "error": True
            })
    
    return {
        "timestamp": datetime.now().isoformat(),
        "count": len(results),
        "stocks": results
    }


# ==================== PARA CORRER LOCALMENTE ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
