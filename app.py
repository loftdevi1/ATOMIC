from flask import Flask, render_template, request
import requests
from datetime import datetime
from textblob import TextBlob

app = Flask(__name__)

# Replace with your Alpha Vantage API key
API_KEY = 'JDNUI7I23A1I9DDC'
NEWS_API_KEY = 'f073a066983a41d18a46d203059357a5'




@app.route('/')
def index():
    return render_template('index.html')




@app.route('/search', methods=['POST'])
def search():
    symbol = request.form['search_symbol']
    exchange = request.form['search_exchange']  # NSE or BSE

    # Map exchange to Alpha Vantage suffix
    exchange_suffix = {
        'NSE': '.NS',
        'BSE': '.BO'
    }.get(exchange, '')

    # Fetch stock data from Alpha Vantage
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}{exchange_suffix}&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()

    # Extract the latest stock price
    time_series = data.get('Time Series (Daily)', {})
    if not time_series:
        return render_template('index.html', error="Invalid symbol or API error.")

    latest_date = list(time_series.keys())[0]
    latest_price = time_series[latest_date]['4. close']

    return render_template('index.html', symbol=symbol, price=latest_price, exchange=exchange)





@app.route('/history', methods=['POST'])
def history():
    print("Form Data:", request.form)  # Debugging step

    if 'history_symbol' not in request.form:
        return render_template('index.html', error="Form data missing. Please fill all fields.")

    symbol = request.form['history_symbol']
    exchange = request.form['history_exchange']
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    # Map exchange to Alpha Vantage suffix
    exchange_suffix = {
        'NSE': '.BOM',  # Alpha Vantage uses .BOM for NSE
        'BSE': '.BSE'
    }.get(exchange, '')

    # Format dates for Alpha Vantage
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

    # Fetch historical data from Alpha Vantage
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}{exchange_suffix}&apikey={API_KEY}&outputsize=full'
    response = requests.get(url)
    data = response.json()

    # Check if data was fetched successfully
    if 'Time Series (Daily)' not in data:
        return render_template('index.html', error="No data found for the given symbol and date range.")

    # Filter data for the given date range
    historical_data = []
    for date_str, values in data['Time Series (Daily)'].items():
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        if start_date_obj <= date_obj <= end_date_obj:
            historical_data.append({
                'Date': date_str,
                'Close': values['4. close']
            })

    if not historical_data:
        return render_template('index.html', error="No data found for the given date range.")

    return render_template('history.html', symbol=symbol, exchange=exchange, data=historical_data)





@app.route('/news', methods=['POST'])
def news():
    symbol = request.form['news_symbol']

    # Fetch news articles using NewsAPI
    url = f'https://newsapi.org/v2/everything?q={symbol}&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    news_data = response.json().get('articles', [])

    # Perform sentiment analysis
    for article in news_data:
        analysis = TextBlob(article.get('description', ''))
        sentiment_score = analysis.sentiment.polarity  # -1 to 1 scale
        article['sentiment'] = sentiment_score

    return render_template('news.html', symbol=symbol, news=news_data)

if __name__ == '__main__':
    app.run(debug=True)