"""  Analyze and create superdarks for COS data

"""


try: from astropy.io import fits as pyfits
except ImportError: import pyfits
import numpy as np
import glob
import os

data_dir = '/grp/hst/cos/Monitors/dark_2/data/'


def lightcurve( filename, step=1 ):
    """ quick one until my lightcurve script works on darks """
    
    SECOND_PER_MJD = 1.15741e-5
 
    hdu = pyfits.open( filename )

    times = hdu['timeline'].data['time'][::step].copy()
    mjd = hdu[1].header['EXPSTART']  + times.copy()[:-1].astype( np.float64 ) *  SECOND_PER_MJD 

    counts = np.histogram( hdu['events'].data['time'], bins=times )[0]

    return counts


def screen_darks( dark_list ):
    """ split darks into baseline and variant"""

    print 'Screening Darks'
    variant_file = open('variant.txt', 'w')
    normal_file = open('normal.txt', 'w')
    empty_file = open('empty.txt', 'w')

    for darkfile in dark_list:
        print darkfile        
        counts = lightcurve( darkfile, step=25 ) 

        if not len(counts):
            empty_file.write('{}\n'.format(darkfile) )
        elif counts.std()/counts.mean() > .3:
            variant_file.write( '{}\n'.format(darkfile) )
        else:
            normal_file.write( '{}\n'.format(darkfile) )

    variant_file.close()
    normal_file.close()


if __name__ == "__main__":
    all_darks = glob.glob( os.path.join( data_dir, '*corrtag*.fits' ) )
    screen_darks( all_darks )

