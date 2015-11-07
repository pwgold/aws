import urllib2
def check_exchange(ticker):
    try:
        html = urllib2.urlopen('https://www.google.com/finance?q=%s'%ticker).read()
        for exchange in ['NYSEMKT','NASDAQ','NYSE','OTCMKTS','OTCBB','NYSEARCA']:
            if '%s:%s'%(exchange,ticker) in html:
                return exchange
    except Exception as e:
        print ticker,e

if __name__ == '__main__':
    import pandas as pd
    import sys, time
    filename = '/home/ubuntu/aws/data/InteractiveBrokers/20151106/usa.txt'
    usa = pd.read_csv(filename, sep='|', skiprows=1, index_col=0)
    tickers = [k for k in usa.index if ' ' not in k] # Skip preferreds by skipping tickers with a space
    for tk in tickers:
        time.sleep(1)
        print '%s,%s'%(tk, check_exchange(tk))
        sys.stdout.flush()
