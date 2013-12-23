import os
import pdb
import glob
import pyfits
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress, normaltest
from scipy.interpolate import griddata
from scipy.signal import medfilt

SECOND_PER_MJD = 1.15741e-5


segment = 'b'

all_lat = []
all_lon = []
all_counts = []
all_times = []
all_sun_lon = []
all_sun_lat = []

def is_variant( counts ):
    #print counts.max(), np.median( counts ) + 3*counts.std(), (counts.max()) > (np.median( counts ) + 3*counts.std())
    return (counts.max()) > (np.median( counts ) + 3*counts.std())

all_std = []
all_sum = []

step = 25

for directory in glob.glob('???3_11_??'):
    print directory
    for name in glob.glob( os.path.join( directory,
                                         '*corrtag_{}.fits'.format( segment ) ) ):
        hdu = pyfits.open( name )
        try:
            times = hdu['timeline'].data['time'][::step].copy()
            lat = hdu['timeline'].data['latitude'].copy()[:-1][::step]
            lon = hdu['timeline'].data['longitude'].copy()[:-1][::step]
            sun_lon = hdu['timeline'].data['sun_lon'].copy()[:-1][::step]
            sun_lat = hdu['timeline'].data['sun_lat'].copy()[:-1][::step]
        except KeyError:
            print 'Not recalibrated'
            continue


        mjd = hdu[1].header['EXPSTART']  + times.copy()[:-1].astype( np.float64 ) *  SECOND_PER_MJD 
        if not len( lat ) > 2:
            print 'too short'
            continue
        if not len( times ) > 2: 
            print 'too short'
            continue

        counts = np.histogram( hdu['events'].data['time'], bins=times )[0]

        spread = counts.std() / counts.sum()
        #if not (spread < .00028): continue
        #if not (spread > .0003): continue

        #if counts.std() > 4.5: continue ## baseline
        #if (counts.std() < 4.5 or counts.std() > 7): continue  ## mid-range/baseline
        if not counts.std() > 90: continue
        all_sum.append( counts.sum() )
        all_std.append( counts.std() )
        #if not is_variant( counts ): continue
        print name, counts.max(), counts.mean(), counts.std(), spread

        hdu.close()
        del hdu

        if not len( lat ) == len(counts):
            lat = lat[:-1]
            lon = lon[:-1]
            sun_lat = sun_lat[:-1]
            sun_lon = sun_lon[:-1]

            #print len(counts), len(lat), len(lon), len(sun_lat), len(sun_lon), len(mjd)

        assert len(lat) == len(counts), 'Arrays are not equal in length {}:{}'.format( len(lat), len(counts) )

        all_lat.append( lat )
        all_lon.append( lon )
        all_sun_lon.append( sun_lon )
        all_sun_lat.append( sun_lat )
        all_counts.append( counts )
        all_times.append( mjd)

all_lat = np.array( all_lat ).flatten()
all_lon = np.array( all_lon ).flatten()
all_sun_lat = np.array( all_sun_lat ).flatten()
all_sun_lon = np.array( all_sun_lon ).flatten()
all_counts = np.array( all_counts ).flatten()
all_times = np.array( all_times ).flatten()
        

all_lat_diff = all_sun_lat - all_lat
all_lon_diff = all_sun_lon - all_lon

#all_lon = np.where( all_lon > 180, all_lon - 360, all_lon )
#all_sun_lon = np.where( all_sun_lon > 180, all_sun_lon - 360, all_sun_lon )

plt.ion()
fig = plt.figure( )#figsize=(20, 12) )
ax = fig.add_subplot( 1,1,1 )
#colors = ax.scatter( all_lon, all_lat, c=all_counts, marker='o', alpha=.7, edgecolors='none', vmin=50)
colors = ax.scatter( all_lon, all_lat, c=all_counts, marker='o', alpha=.7, edgecolors='none', 
                     s=3, lw=0, vmin=all_counts.min(), vmax=all_counts.min() + 3*all_counts.std() )
fig.colorbar( colors )


fig2 = plt.figure()
ax2 = fig2.add_subplot( 1,1,1 )
ax2.plot( all_times, all_counts, 'o' )


fig3 = plt.figure( )#figsize=(20, 12) )
ax3 = fig3.add_subplot( 1,1,1 )
colors = ax3.scatter( all_lon_diff, all_lat_diff, c=all_counts, marker='o', alpha=.7, edgecolors='none', s=5, lw=0, 
                      vmax=all_counts.min() + 3*all_counts.std() )


gridx, gridy = np.mgrid[all_lon.min():all_lon.max():.1, all_lat.min():all_lat.max():.1]
thing = griddata( zip(all_lon, all_lat), all_counts, (gridx, gridy), method='nearest' )
image = medfilt( thing.T, (5,5) )
fig4 = plt.figure()
ax4 = fig4.add_subplot( 1,1,1 )
cax = ax4.imshow( image, aspect='auto', interpolation='nearest', vmin=all_counts.min(), vmax=all_counts.min() + 3*all_counts.std()  )
fig4.colorbar( cax )

pdb.set_trace()
