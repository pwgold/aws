import sys
sys.path.append('/home/ubuntu/aws/src/')

'''
   262 Non-marginable stocks are not allowed for short sell
     26 Opening transactions for this security must be placed with a broker. Please contact us.
   2394 Shares of this security are currently not available to short sell
    185 The system is temporarily unavailable
      1 This order could not be placed
   2402 You cannot short sell OTC Bulletin Board securities
      1 You do not have enough available cash/buying power for this order
      2 Your order was not accepted. Funds are not available
   2513 Your order was received
'''

from BeautifulSoup import BeautifulSoup
import mech
import time

''' 
Script to check short availability (borrows) at Ameritrade. 
Input should be either:
    '--tickers' followed by a list of tickers (without commas), or 
    '--file' followed by a filename.
For each ticker, the script will print to the screen:
    ticker, 0 or 1, text reason
with a 1 if the stock is available to borrow and 0 if it's not.
'''

def print_usage():
        raise Exception('Input argument should be --tickers or --file' + '\n' + 
                        'E.g., python Ameritrade.py --tickers ATPG CALL HK JKS JRCC KSS MDP MEET NAT OIBR RRD SKUL TSTC YELP JVA WPRT ARNA' + '\n' + 
                        'or    python Ameritrade.py --file tickers.csv')

'''
Parse input. Raise exception if list of tickers is not retrieved correctly
'''
tickers = []
if len(sys.argv) <= 1:
    print_usage()
else:
    if sys.argv[1] == '--tickers':
        tickers = sys.argv[2:]
    elif sys.argv[1] == '--file':
        filename = sys.argv[2]
        with open(filename) as f:
            tickers = [r.rstrip('\n') for r in f]
    else:
        print_usage()
    
    if len(tickers) == 0:
        raise Exception('No tickers were found')
    #else:
    #    print 'Fetching: %s' % ','.join(tickers)

'''
Get browser, and log in to Ameritrade. 
Replace userid and password below with correct values. 
TODO: o Encrypt so they are not stored in plain text.
'''
(br,__) = mech.get_browser()
br.open('https://mobile.tdameritrade.com/wireless/loginAction_input.action')
html = br.response().read()
assert 'Password' in html, 'Not on logon page'
assert 'Ameritrade' in html
# print html
br.select_form(nr=0)
br['userid'] = 'pwgold3957'
br['password'] = 'Ar1thm3t1cF00'
br.submit()
assert 'Balances' in br.response().read(), 'not on login landing page: %s'%br.response().read()

'''
Gather list of possible responses / errors you may see when you try to submit a Sell Short order.
'''
bad_sym_cond = []
cond = []
# Invalid Symbol -- These issues can appear first, and if they do you don't submit an order.
bad_sym_cond.append('The Security Symbol is Invalid')
bad_sym_cond.append('The symbol could not be found. Please contact a Broker for assistance with this order')
bad_sym_cond.append('Invalid Symbol. Please enter valid symbol')
bad_sym_cond.append('Security Not Found')
# just add the bad system message here as well, it *should* mean you didn't place an order
bad_sym_cond.append('The system is temporarily unavailable, please try your request again later.')
bad_sym_cond.append('Order entry failed. Error Unknown.')
# Available
cond0 = 'Your order was received' # E.g., Your Limit Order to Sell Short 1 share of spy  at  500.00 was received.
cond0B = 'Your order no. is'
cond1 = 'Short sale orders are not allowed'
# Not Available
cond.append('The system is temporarily unavailable, please try your request again later')
cond.append('Shares of this security are currently not available to short sell')
cond.append('You cannot short sell OTC Bulletin Board securities')
cond.append('Non-marginable stocks are not allowed for short sell')
cond.append('Opening transactions for this security must be placed with a broker. Please contact us.')
# Invalid Price
cond.append('Invalid Price. Please enter valid Price.')
cond.append('Your limit is significantly below the bid or last. Please confirm you are selling the correct security.')
# Not enough buying power
cond.append('Your order was not accepted. Funds are not available')
cond.append('You do not have enough available cash/buying power for this order')
# Anonymous error
cond.append('This order could not be placed')

cond.extend(bad_sym_cond) # Note: Bad symbol issues (maybe just 'Security Not Found') can appear only after you submit the order

'''
Loop over tickers, submit an unmarketable Sell Short order for 1 share, and 
print whether the stock was available to borrow and the condition (explanation) you encountered.
If the stock is availale and you submitted the order, cancel the order, and throw an exception if you weren't able to cancel.
'''
output = []
for tk in tickers:
    try:
        time.sleep(1)
        br.open('https://mobile.tdameritrade.com/wireless/equityOrderAction_input.action?orderObj.security.symbol=')
        br.select_form(nr=0)
        br['orderObj.action']=['Sell Short']
        br['orderObj.quantity']='1'
        br['orderObj.security.symbol']=tk
        br['orderObj.orderType']=['Limit']
        br.submit()
        
        html = br.response().read()
        true_bad_sym_conditions = [c in html for c in bad_sym_cond]
        assert sum(true_bad_sym_conditions) < 2, 'More than 2 true conditions? Do we have duplicates?'
        if any(true_bad_sym_conditions):
            explanation = bad_sym_cond[true_bad_sym_conditions.index(True)]
            line = '%s,%s,%s' %(tk,0,explanation)   
            output.append(line)
            print line
            continue
            
        assert 'Step 2 of 2' in br.response().read(), 'Not on Step 2 of trading\n%s' % br.response().read()
        br.select_form(nr=0)
        
        # Get Ask price from html, and set limit order price to 2x the last ask
        idx = br.response().read().index('Ask')
        ask_str = br.response().read()[idx+len('Ask</b>:'):]
        ask = float(ask_str[0:ask_str.index('<')].lstrip(' ').replace(',',''))
        
        # If last ask was 0, use a limit price of 100
        if ask == 0:
            br['orderObj.limitPrice']='100'
        else:
            br['orderObj.limitPrice']=str(ask * 2)
        br.submit()
                    
        br.select_form(nr=0) # TODO: o Check what form / button you're clicking here.
        br.submit()
    
        ''' 
        Read the html response. If cond0 or cond1 are seen, the stock was available..
        If no conditions were seen, raise an exception, and look at the html to see the new condition (error message) 
        that should be added above.
        '''
        html = br.response().read()
        true_conditions = [c in html for c in cond]
        if cond0 in html or cond0B in html:
            available = 1
            explanation = cond0
            order_no = BeautifulSoup(html).findAll('b')[6].text
            br.open('https://mobile.tdameritrade.com/wireless/cancelOrderConfirmationAction.action?orderId='+order_no)
            html = br.response().read()
            #if 'Please press back/cancel button of your cell/pda for previous page' not in html:
            # 'There was a problem canceling the order.(Order11984813329)'
            # Get this message for JKS -- order is accepted and then cancelled after Pending Review
            # Also saw: The system is temporarily unavailable, please try your request again later
            assert 'was submitted for cancellation' in html, 'Order not cancelled:\n%s' % html  # Here's where we cancel the submitted order.
        #elif cond0B in html:
        #    available = 1
        #    explanation = cond0B
        #    order_no = BeautifulSoup(html).findAll('b')[6].text
        #    br.open('https://mobile.tdameritrade.com/wireless/cancelOrderConfirmationAction.action?orderId='+order_no)
        #    html = br.response().read()
        #    assert 'was submitted for cancellation' in html, 'Order not cancelled:\n%s' % html  # Here's where we cancel the submitted order.
        elif cond1 in html:
            available = 1
            explanation = cond1
        else:
            true_conditions = [c in html for c in cond]
            assert sum(true_conditions) < 2, 'More than 2 true conditions were met? They are meant to be mutually exclusive.'
            if any(true_conditions):
                explanation = cond[true_conditions.index(True)]
                available = 0
            else:
                raise Exception(html)

        line = '%s,%s,%s,%s' %(tk,available,explanation,ask)
        output.append(line)
        print line
    except Exception as e:
        print tk,e
        sys.stdout.flush()

import pandas as pd
filename = pd.datetime.now().strftime('%s')+'.csv'
data_dir = '/home/ubuntu/aws/data/Ameritrade'
pd.Series(output).to_csv('%s/%s'%(data_dir,filename))
