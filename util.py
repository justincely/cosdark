def cat_corrtag(input_list):
    all_exptime = [ pyfits.getval(item,'EXPTIME',ext=1) for item in input_list ]
    events_data = [ pyfits.getdata(item,'EVENTS') for item in input_list ]

    total = 0 
    for i, exptime in enumerate( all_exptime[:-1] ):
        for j in range(len(events_data[i+1]['TIME'])):
            events_data[i+1]['TIME'][j] += exptime + total
            
        total += exptime

    all_data = np.concatenate( (events_data),axis=0 )
    tab = pyfits.BinTableHDU(data = all_data)

    return tab
