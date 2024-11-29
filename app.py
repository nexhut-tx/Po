from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
from ta import momentum, trend, volatility  # TA-Lib alternative

app = Flask(__name__)

# Sample data for testing (usually you'd fetch this from an API)
data = {
    'time': pd.date_range(start='1/1/2024', periods=100, freq='T'),
    'close': np.random.random(100) * 100 + 150  # Random close price
}

df = pd.DataFrame(data)

def analyze_data(df):
    # Calculate RSI
    df['RSI'] = momentum.rsi(df['close'], window=14)
    
    # Calculate EMAs
    df['EMA_50'] = trend.ema_indicator(df['close'], window=50)
    df['EMA_200'] = trend.ema_indicator(df['close'], window=200)
    
    # Calculate Bollinger Bands
    df['Bollinger_Upper'], df['Bollinger_Lower'] = volatility.bollinger_hband(df['close']), volatility.bollinger_lband(df['close'])
    
    # Generate signals
    df['Signal'] = 'HOLD'
    df.loc[(df['RSI'] < 30) & (df['EMA_50'] > df['EMA_200']), 'Signal'] = 'BUY'
    df.loc[(df['RSI'] > 70) & (df['EMA_50'] < df['EMA_200']), 'Signal'] = 'SELL'
    
    return df

@app.route('/api/signals', methods=['GET'])
def get_signals():
    frequency = request.args.get('frequency', '1m')  # Default to 1 minute
    signals_df = analyze_data(df)
    
    # For now, just return the latest signal
    latest_signal = signals_df[['time', 'Signal']].iloc[-1]
    
    return jsonify({
        'time': latest_signal['time'].strftime('%Y-%m-%dT%H:%M:%SZ'),
        'signal': latest_signal['Signal'],
        'confidence': 90  # For simplicity, setting confidence to 90%
    })

if __name__ == '__main__':
    app.run(debug=True)
