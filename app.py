from flask import Flask, jsonify, request
from pocketoptionapi.stable_api import PocketOption
import pandas as pd
import numpy as np
import time
import os

app = Flask(__name__)

# Pocket Option Authentication
def authenticate():
    ssid = os.getenv('POCKET_OPTION_SSID')  # Get ssid from environment variable
    if not ssid:
        raise ValueError("Session ID (SSID) is missing.")
    
    account = PocketOption(ssid)
    check_connect, message = account.connect()
    
    if not check_connect:
        return jsonify({"error": "Failed to authenticate with Pocket Option", "message": message}), 400
    return account

# Function to fetch the market data (Candlestick data)
def fetch_market_data(asset="EURUSD"):
    account = authenticate()
    current_time = int(time.time())
    offset = 120  # Time offset in seconds
    period = 60  # Candlestick period in seconds
    candles = account.get_candle(asset, current_time, offset, period)
    return candles["data"]

# Technical Analysis Logic to generate signals
def analyze_data(df):
    df['RSI'] = pd.Series(np.random.random(len(df)), index=df.index)  # Example RSI (Replace with actual logic)
    df['EMA_50'] = df['Close'].ewm(span=50).mean()
    df['EMA_200'] = df['Close'].ewm(span=200).mean()

    # Generating Buy/Sell signals based on strategy
    df['Signal'] = 'HOLD'
    df.loc[(df['RSI'] < 30) & (df['EMA_50'] > df['EMA_200']), 'Signal'] = 'BUY'
    df.loc[(df['RSI'] > 70) & (df['EMA_50'] < df['EMA_200']), 'Signal'] = 'SELL'
    
    return df

@app.route('/api/signals', methods=['GET'])
def get_signals():
    symbol = request.args.get('symbol', 'EURUSD')  # Default to EURUSD if no symbol provided
    
    # Fetch market data (candlestick data for the asset)
    data = fetch_market_data(symbol)
    df = pd.DataFrame(data)
    
    # Analyze market data to generate signals
    signals_df = analyze_data(df)
    
    # Returning the latest signal
    latest_signal = signals_df[['time', 'Signal']].iloc[-1]
    
    return jsonify({
        'time': latest_signal['time'],
        'signal': latest_signal['Signal'],
        'confidence': 90  # For simplicity, confidence is set to 90
    })

@app.route('/api/trade', methods=['POST'])
def place_trade():
    symbol = request.json.get('symbol', 'EURUSD')
    amount = request.json.get('amount', 1)
    direction = request.json.get('direction', 'call')  # 'put' or 'call'
    duration = request.json.get('duration', 60)  # In seconds
    
    account = authenticate()
    
    # Place the trade using Pocket Option API
    trade_info = account.buy(symbol, amount, direction, duration)
    
    return jsonify({
        'message': 'Trade placed successfully',
        'trade_info': trade_info
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
