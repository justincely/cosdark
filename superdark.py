""" Class to hold each superdark reference file """

from astropy.io import fits as pyfits
import numpy as np

class SuperDark( object ):
    def __init( self, segment ):
        if segment in ['FUVA', 'FUVB']:
            shape = (1024, 16384)
        elif segment == 'NUV':
            shape = (1025, 1024)
        else:
            raise ValueError( "{} not in FUVA, FUVB, NUV".format( detector )

        self.detector = detector[:3]
        self.segment = detector

        self.included_files = []
        self.expstart = -1
        self.expend = -1
        
        self.events = None

    def write( outname, clobber=False ):
        pass
