_=''' Usage:
python list_ib_tickers.py ../data/InteractiveBrokers/20151106/usa.txt
'''

import InteractiveBrokers
import sys

if __name__ == '__main__':
    input_file = sys.argv[1]
    ib = InteractiveBrokers.InteractiveBrokers()
    df = ib.read_file(input_file)
    tickers = df.sort(columns='REBATERATE').index
    tickers = [e for e in tickers if ' ' not in e and '#' not in e] # skipping preferreds (e.g., "A PR") and #EOF
    print ' '.join(tickers)
