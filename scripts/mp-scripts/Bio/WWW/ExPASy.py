# Copyright 2000 by Jeffrey Chang.  All rights reserved.
# This code is part of the Biopython distribution and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.

"""
This module provides code to access resources at ExPASy over the WWW.
http://www.expasy.ch/


Functions:
get_prodoc_entry  Interface to the get-prodoc-entry CGI script.
get_prosite_entry Interface to the get-prosite-entry CGI script.
get_prosite_raw   Interface to the get-prosite-raw CGI script.
get_sprot_raw     Interface to the get-sprot-raw CGI script.
sprot_search_ful  Interface to the sprot-search-ful CGI script.
sprot_search_de   Interface to the sprot-search-de CGI script.
_open

"""

import warnings
warnings.warn("Bio.WWW.ExPASy is deprecated. The functions in Bio.WWW.ExPASy  are now available from Bio.ExPASy.",
              DeprecationWarning)


def get_prodoc_entry(id, cgi='http://www.expasy.ch/cgi-bin/get-prodoc-entry'):
    """get_prodoc_entry(id,
    cgi='http://www.expasy.ch/cgi-bin/get-prodoc-entry') -> handle

    Get a handle to a PRODOC entry at ExPASy in HTML format. 

    For a non-existing key XXX, ExPASy returns a web page containing
    this line:
    'There is no PROSITE documentation entry XXX. Please try again.'
    """
    # XXX need to check to see if the entry exists!
    return _open("%s?%s" % (cgi, id))

def get_prosite_entry(id,
                      cgi='http://www.expasy.ch/cgi-bin/get-prosite-entry'):
    """get_prosite_entry(id,
    cgi='http://www.expasy.ch/cgi-bin/get-prosite-entry') -> handle

    Get a handle to a PROSITE entry at ExPASy in HTML format.

    For a non-existing key XXX, ExPASy returns a web page containing
    this line:
    'There is currently no PROSITE entry for XXX. Please try again.'
    """
    # XXX need to check to see if the entry exists!
    return _open("%s?%s" % (cgi, id))

def get_prosite_raw(id, cgi='http://www.expasy.ch/cgi-bin/get-prosite-raw.pl'):
    """get_prosite_raw(id,
                       cgi='http://www.expasy.ch/cgi-bin/get-prosite-raw.pl')
    -> handle

    Get a handle to a raw PROSITE or PRODOC entry at ExPASy.

    For a non-existing key, ExPASy returns nothing.
    """
    import urllib, socket
    handle = urllib.urlopen("%s?%s" % (cgi, id))

    # Peek at the first character to see if anything is available.
    # ExPASy returns nothing for non-existing keys

    start = handle.fp._sock.recv(1, socket.MSG_PEEK)
    if not start: # ExPASy returned nothing
        raise IOError, "no results"

    return handle

def get_sprot_raw(id, cgi='http://www.expasy.ch/cgi-bin/get-sprot-raw.pl'):
    """get_sprot_raw(id, cgi='http://www.expasy.ch/cgi-bin/get-sprot-raw.pl')
    -> handle

    Get a handle to a raw SwissProt entry at ExPASy.

    For a non-existing key XXX, ExPASy returns a web page containing
    this line:
    'XXX is not a valid identifier.'
    """
    return _open("%s?%s" % (cgi, id))

def sprot_search_ful(text, make_wild=None, swissprot=1, trembl=None,
                     cgi='http://www.expasy.ch/cgi-bin/sprot-search-ful'):
    """sprot_search_ful(text, make_wild=None, swissprot=1, trembl=None,
    cgi='http://www.expasy.ch/cgi-bin/sprot-search-ful') -> handle

    Search SwissProt by full text.

    """
    variables = {'SEARCH' : text}
    if make_wild:
        variables['makeWild'] = 'on'
    if swissprot:
        variables['S'] = 'on'
    if trembl:
        variables['T'] = 'on'
    return _open(cgi, variables)

def sprot_search_de(text, swissprot=1, trembl=None,
                    cgi='http://www.expasy.ch/cgi-bin/sprot-search-de'):
    """sprot_search_de(text, swissprot=1, trembl=None,
    cgi='http://www.expasy.ch/cgi-bin/sprot-search-de') -> handle

    Search SwissProt by name, description, gene name, species, or
    organelle.

    """
    variables = {'SEARCH' : text}
    if swissprot:
        variables['S'] = 'on'
    if trembl:
        variables['T'] = 'on'
    return _open(cgi, variables)

def scanprosite1(seq=None, id=None, exclude_frequent=None, 
                 cgi='http://expasy.cbr.nrc.ca/cgi-bin/scanprosite/scanprosite?1'):
    """scanprosite1(seq=None, id=None, exclude_frequent=None, 
    cgi='http://expasy.cbr.nrc.ca/cgi-bin/scanprosite/scanprosite?1') -> handle
    
    Scan a sequence for a Prosite pattern.  Either a sequence or a SwissProt/
    trEMBL sequence can be passed.  exclude_frequent specifies whether to
    exclude patterns with high probability.
    
    """
    variables = {}
    if seq:
        variables['SEQ'] = seq
    if id:
        variables['ID'] = id
    if exclude_frequent:
        variables['box'] = 'ok'
    return _open(cgi, variables, get=0)

def _open(cgi, params={}, get=1):
    """_open(cgi, params={}, get=1) -> UndoHandle

    Open a handle to ExPASy.  cgi is the URL for the cgi script to access.
    params is a dictionary with the options to pass to it.  get is a boolean
    that describes whether a GET should be used.  Does some
    simple error checking, and will raise an IOError if it encounters one.

    """
    import urllib
    from Bio import File

    # Open a handle to ExPASy.
    options = urllib.urlencode(params)
    if get:  # do a GET
        fullcgi = cgi
        if options:
            fullcgi = "%s?%s" % (cgi, options)
        handle = urllib.urlopen(fullcgi)
    else:    # do a POST
        handle = urllib.urlopen(cgi, options)

    # Wrap the handle inside an UndoHandle.
    uhandle = File.UndoHandle(handle)

    # If the key doesn't exist, ExPASy returns nothing.
    if not uhandle.peekline():
        raise IOError, "no results"
    
    return uhandle
