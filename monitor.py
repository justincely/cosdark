"""  Analyze and create superdarks for COS data

"""


try: from astropy.io import fits as pyfits
except ImportError: import pyfits
import numpy as np
import glob
import os
from superdark import SuperDark

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


def create_superdarks( file_list ):
    print 'Creating superdarks'
    all_mjd = [pyfits.getval(item, 'EXPSTART', ext=1 ) for item in file_list ]
    
    file_list = np.array( file_list )
    all_mjd = np.array( all_mjd )

    step = 30
    first_mjd = int(all_mjd.min())
    end_mjd = int(all_mjd.max())
    print 'Running from ', first_mjd, end_mjd

    for start in range( first_mjd, end_mjd, step)[:-1]:
        print start, '-->', start+step
        file_index = np.where( (all_mjd > start) &
                               (all_mjd < start+step) )[0]
        if not len( file_index ):
            print 'WARNING, no files found for interval'
 
        dark_reffile = SuperDark( file_list[ file_index ] )
        output = '{}_{}_drk.fits'.format( start, start+step )
        dark_reffile.write( outname=output )
        pyfits.setval( output, 'DATASTRT', ext=0, value=start )
        pyfits.setval( output, 'DATAEND', ext=0, value=start+step )
        

if __name__ == "__main__":
    all_darks = glob.glob( os.path.join( data_dir, '*corrtag*.fits' ) )
    screen_darks( all_darks )

    baseline_darks = np.genfromtxt('normal.txt', dtype=None )
    create_superdarks( baseline_darks )
    
