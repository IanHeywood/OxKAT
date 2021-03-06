# ian.heywood@physics.ox.ac.uk
# UHF calibration is experimental


import glob
import pickle
import shutil
import time


execfile('oxkat/casa_read_project_info.py')
execfile('oxkat/config.py')



tb.open(myms)
colnames = tb.colnames()
tb.done()



# ------- Setjy models


if primary_tag == '1934':
    setjy(vis=myms,
        field=bpcal_name,
        standard='Stevens-Reynolds 2016',
        scalebychan=True,
        usescratch=True)
    
    
elif primary_tag == '0408':
    bpcal_mod = [27.907, 0.0, 0.0, 0.0],[-1.205],'850MHz')
    setjy(vis=myms,
        field=bpcal_name,
        standard='manual',
        fluxdensity=bpcal_mod[0],
        spix=bpcal_mod[1],
        reffreq=bpcal_mod[2],
        scalebychan=True,
        usescratch=True)


elif primary_tag == 'other':
    setjy(vis=myms,
        field=bpcal_name,
        standard='Perley-Butler 2010',
        scalebychan=True,
        usescratch=True)