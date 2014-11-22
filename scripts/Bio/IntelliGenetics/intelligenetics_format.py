# Copyright 2001 by Katharine Lindner.  All rights reserved.
# This code is part of the Biopython distribution and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.

"""Martel regular expression for Intelligenetic format.

http://hiv-web.lanl.gov/ALIGN_97/HIV12SIV-index.html
"""
# standard library
#http://immuno.bme.nwu.edu/seqhunt.html
import string

# Martel
import Martel
from Martel import RecordReader

# --- first set up some helper constants and functions
comment_line = Martel.Group( "comment_line", \
                             Martel.Str( ';' ) +
                             Martel.ToEol( "comment" ) )
comment_lines = Martel.Group( "comment_lines", Martel.Rep( comment_line ) )
title_line = Martel.Group( "title_line", \
    Martel.Expression.Assert( Martel.Str( ';' ), 1 ) +
    Martel.ToEol() )
residue_line = Martel.Group( "residue_line", \
    Martel.Expression.Assert( Martel.Str( ';' ), 1 ) +
    Martel.ToEol( "sequence" ) )
residue_lines = Martel.Group( "residue_lines", Martel.Rep1( residue_line ) )
intelligenetics_record =  comment_lines + title_line + residue_lines
