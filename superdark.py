""" Class to hold each superdark reference file """

from astropy.io import fits as pyfits
import numpy as np

class SuperDark( object ):
    def __init__( self, file_list ):
        print 'Building superdark form file list'
	detector = pyfits.getval( file_list[0], 'DETECTOR' )

        self.detector = detector[:3]
        self.segment = detector

        self.included_files = file_list
        self.expstart = -1
        self.expend = -1
        
        self.events_a = cat_corrtag( [item for item in file_list 
                                      if '_corrtag_a' in item] )
        self.events_b = cat_corrtag( [item for item in file_list 
                                      if '_corrtag_b' in item] )

    def write(self, outname, clobber=False ):
        hdu = pyfits.HDUList(pyfits.PrimaryHDU())
        hdu[0].header['INSTRUME'] = 'COS'
        hdu[0].header['DETECTOR'] = 'FUV'

        hdu.append(pyfits.new_table(self.events_a) )
        hdu[1].header['SEGMENT'] = 'FUVA'

        hdu.append(pyfits.new_table(self.events_b) )
        hdu[2].header['SEGMENT'] = 'FUVB'

        hdu.writeto(outname, clobber=clobber)

def cat_corrtag(input_list):
    all_exptime = [ pyfits.getval(item,'EXPTIME',ext=1) for item in input_list ]
    events_data = [ pyfits.getdata(item,'EVENTS') for item in input_list ]

    total = 0 
    for i, exptime in enumerate( all_exptime[:-1] ):
        for j in range(len(events_data[i+1]['TIME'])):
            events_data[i+1]['TIME'][j] += exptime + total
            
        total += exptime

    all_data = np.concatenate( (events_data),axis=0 )

    return all_data
