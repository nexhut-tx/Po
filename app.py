import talib
import numpy as np
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Function to fetch market data
def get_market_data(symbol, interval='1m'):
    # Replace this with real market data fetching logic from your source
    # For demonstration, we're using dummy data.
    return [
        {'close': 1.100},
        {'close': 1.102},
        {'close': 1.104},
        {'close': 1.106},
        {'close': 1.108},
        {'close': 1.110},
    ]

# Function to generate trading signal based on strategy
def generate_signal(data, interval='1m'):
    close_prices = np.array([entry['close'] for entry in data])

    # Calculate Simple Moving Average (SMA) for 5 and 20 periods
    short_sma = talib.SMA(close_prices, timeperiod=5)
    long_sma = talib.SMA(close_prices, timeperiod=20)
    
    # Simple Strategy: Signal if there's a crossover of SMA
    signal = "HOLD"
    confidence = 0

    if short_sma[-1] > long_sma[-1]:
        signal = "BUY"
        confidence = 90  # Set to 90% confidence
    elif short_sma[-1] < long_sma[-1]:
        signal = "SELL"
        confidence = 90  # Set to 90% confidence
    
    return signal, confidence

@app.route('/get_signal', methods=['GET'])
def get_signal():
    symbol = "BTCUSD"  # Example symbol, you can change based on your market
    interval = "1m"    # Example interval, 1m, 3m, 5m, etc.
    
    market_data = get_market_data(symbol, interval)
    signal, confidence = generate_signal(market_data, interval)
    
    return jsonify({
        'symbol': symbol,
        'interval': interval,
        'signal': signal,
        'confidence': confidence
    })

if __name__ == '__main__':
    app.run(debug=True)
