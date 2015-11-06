''' all imports '''

import os, sys, re, csv, urllib2, collections
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
try:
    import scikits.timeseries as ts
    import scikits.timeseries.lib.plotlib as tpl
    import scikits.statsmodels.api as sm
except:
    print 'Exception'

from BeautifulSoup import BeautifulSoup

#try:
#    from pyExcelerator import parse_xls
#except:
#    print 'No pyExcelerator'

import simplejson

def progress( message ):
    sys.stdout.write('\r')
    sys.stdout.write( message )
    sys.stdout.flush()



def get_html( url ):
    return urllib2.urlopen( url ).read()

def get_soup( url ):
    return BeautifulSoup( urllib2.urlopen( url ).read() )

def get_xls( url, use_file=False ):
    try:
        if use_file:
            fh = open(file)
            data = parse_xls(fh, 'cp1251')
            fh.close()
            return data
        else:
            return parse_xls( urllib2.urlopen( url ), 'cp1251')
    except:
        print 'No get_xls'

def get_json_data( url, default_return=[], use_file=False ):
    ''' Dictionary keys may not be quoted, so HERE we fix this.
    x Find everything between ',KEY:' and '{KEY:' and replace KEY with "KEY"
    x Return [] if html was ''
    TODOs
    '''
    if use_file: # Read from disk if url was really a filenames
        fh = open( url )
        html = fh.read()
        fh.close()
    else:
        html = urllib2.urlopen( url ).read()
    
    if html == '':
        return default_return
    else:
        try:
            data = simplejson.loads( html )
        except Exception,e:
            if type(e) == simplejson.decoder.JSONDecodeError:
                pass # TODO: Fix
            else:
                print 'PETE: Warning, exception %s loading json data, type=%s' %(e,type(e))
            key_pat = re.compile('.*([{,]([a-z_]*):)')
            match = key_pat.match(html)
            while match != None:
                grps = match.groups()
                html = html.replace( grps[0], '%s"%s"%s' %(grps[0][0], grps[1], grps[0][-1]))
                match = key_pat.match(html)
            data = simplejson.loads( html )
        return data

def get_csv( file_name , delimiter=','):
	fh = open( file_name )
	data = [r for r in csv.reader(fh,delimiter=delimiter) ]
	fh.close()
	return data 
 
def get_dict( file_name , delimiter=','):
    fh = open( file_name )
    data = [ r for r in csv.DictReader( fh , delimiter=delimiter) ]
    fh.close()
    return data

''' From http://www.scipy.org/Cookbook/InputOutput#head-b0366eac0be19c3d7c32fc81c47a7c02508b6f52
Usage:
mydescr = N.dtype([('column1', 'int32'), ('column2Name', 'uint32'), ('col3', 'uint64'), ('c4', 'float32')])
myrecarray = read_array('file.csv', mydescr)
'''
def get_array(filename, dtype, separator=','):
    """ Read a file with an arbitrary number of columns.
        The type of data in each column is arbitrary
        It will be cast to the given dtype at runtime
    """
    cast = N.cast
    data = [[] for dummy in xrange(len(dtype))]
    for line in open(filename, 'r'):
        fields = line.strip().split(separator)
        for i, number in enumerate(fields):
            data[i].append(number)
    for i in xrange(len(dtype)):
        data[i] = cast[dtype[i]](data[i])
    return N.rec.array(data, dtype=dtype)

def convert_timestamp( ts, fmt='%Y-%m-%d %H:%M:%S' ):
    # Convert From Unix Timestamp
    return datetime.fromtimestamp(int(ts)).strftime(fmt)
    
def get_date( datestr, fmt='%Y%m%d', ts_freq=None ):
    datestr = datestr.replace('-', '')
    if ts_freq != None:
        return ts.Date(ts_freq, datestr) #e.g., 'B'
    else:
        return datetime.strptime( datestr, '%Y%m%d' )

def daterange( format='%Y%m%d', start='19690101', end=None, delta=None ):
    ''' Return array of dates in range. Try with end='19690201' or delta=30 '''
    #if type(start) == type(''):
    #    start = datetime.strptime( start, format )
    if end and delta:
        assert False, 'Input arguments <end> and <delta> should not both be set.'
    elif end:
        end = datetime.strptime( end, format )
    elif delta:
        end = start + timedelta(delta)
    else:
        assert False, 'Either <end> or <delta> must be set'
    start = datetime.strptime( start, format )
    dates = [ (start + timedelta(i)).strftime( format ) for i in range((end-start).days) ]
    dates.sort()
    dates.reverse() # [ Current date first ... earliest date last ]
    return dates

