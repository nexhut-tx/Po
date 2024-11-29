import os
import pandas as pd
import pandas_ta as ta
from flask import Flask, jsonify, request

app = Flask(__name__)

# Function to fetch market data
def get_market_data(symbol, interval='1m'):
    otc_symbols = ["OTC_AAPL", "OTC_TSLA", "OTC_AMZN", "OTC_GOOG", "OTC_MSFT", "OTC_NFLX"]
    
    if symbol in otc_symbols:
        # Simulate different market data for OTC stocks
        return [
            {'close': 150.00},  # Example for Apple (AAPL)
            {'close': 152.00},
            {'close': 154.00},
            {'close': 156.00},
            {'close': 158.00},
            {'close': 160.00},
        ]
    
    # Regular symbols (like BTCUSD, ETHUSD)
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
    close_prices = [entry['close'] for entry in data]
    df = pd.DataFrame({'close': close_prices})
    df['short_sma'] = ta.sma(df['close'], length=5)
    df['long_sma'] = ta.sma(df['close'], length=20)

    if pd.isna(df['short_sma'].iloc[-1]) or pd.isna(df['long_sma'].iloc[-1]):
        return "HOLD", 0  # If the SMA is NaN, don't generate a signal

    signal = "HOLD"
    confidence = 0
    if df['short_sma'].iloc[-1] > df['long_sma'].iloc[-1]:
        signal = "BUY"
        confidence = 90  # Confidence level
    elif df['short_sma'].iloc[-1] < df['long_sma'].iloc[-1]:
        signal = "SELL"
        confidence = 90  # Confidence level

    return signal, confidence

@app.route('/')
def index():
    return app.send_static_file('index.html')  # Make sure index.html is in the correct folder

@app.route('/get_signal', methods=['GET'])
def get_signal():
    # Get the query parameters from the request
    symbol = request.args.get('symbol', 'BTCUSD')  # Default to 'BTCUSD' if no symbol is provided
    interval = request.args.get('interval', '1m')  # Default to '1m' if no interval is provided

    # Fetch market data based on the symbol and interval
    market_data = get_market_data(symbol, interval)
    signal, confidence = generate_signal(market_data, interval)

    return jsonify({
        'symbol': symbol,
        'interval': interval,
        'signal': signal,
        'confidence': confidence
    })

if __name__ == '__main__':
    # Get the port from the environment variable, default to 5000 if not set
    port = int(os.environ.get('PORT', 5000))  # Render dynamically assigns a port number

    # Run Flask app on the correct host and port
    app.run(debug=True, host='0.0.0.0', port=port)
