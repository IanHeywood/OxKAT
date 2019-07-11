#!/usr/bin/env python
# ian.heywood@physics.ox.ac.uk


import glob
import datetime
import time
import os


CWD = os.getcwd()
OXKAT = CWD+'/oxkat'
SCRIPTS = CWD+'/scripts'
LOGS = CWD+'/logs'
PARSETS = CWD+'/parsets'


CASA_CONTAINER = '/data/exp_soft/containers/casa-stable-5.4.1-31.simg'
WSCLEAN_CONTAINER = '/data/exp_soft/containers/kern4-2018-11-28.simg'
CUBICAL_CONTAINER = '/data/exp_soft/containers/kern4-2018-11-28.simg'
DDFACET_CONTAINER = '/users/ianh/containers/ddf/...'
KILLMS_CONTAINER = '/users/ianh/containers/ddf/...'
CODEX_CONTAINER = '...'
SOURCEFINDER_CONTAINER = '/data/exp_soft/containers/SF-PY3-bionic.simg'


#CUBICAL_EXEC = '/users/ianh/venv/cubical/bin/python2.7 /users/ianh/venv/cubical/bin/gocubical'
CUBICAL_EXEC = 'gocubical'

TRICOLOUR_VENV = '/users/ianh/venv/tricolour/bin/activate'

#DOT_LOCAL_BIN = '/users/ianh/.local/bin'

# ------------------------------------------------------------------------


def setup_scripts_dir():

    # Make scripts folder if it doesn't exist

    if not os.path.isdir(SCRIPTS):
        os.mkdir(SCRIPTS)


def timenow():

    # Return a date and time string suitable for being part of a filename

    now = str(datetime.datetime.now()).replace(' ','-').replace(':','-').split('.')[0]
    return now


def get_code(myms):

    # Last three digits of the data set ID, plus the sub-band

    myms = myms.split('/')[-1]

    if 'HI' in myms:
        band = 'H'
    elif 'LO' in myms:
        band = 'L'
    else:
        band = 'F'

    code = myms.split('_')[0][-3:]

    return code+band


def make_executable(infile):

    # https://stackoverflow.com/questions/12791997/how-do-you-do-a-simple-chmod-x-from-within-python

    mode = os.stat(infile).st_mode
    mode |= (mode & 0o444) >> 2
    os.chmod(infile, mode)


# ------------------------------------------------------------------------


def write_slurm(opfile,
                jobname,
                ntasks='1',
                nodes='1',
                cpus='32',
                mem='230GB',
                logfile,
                container,
                syscall):

    # Generate slurm script 

    f = open(opfile,'w')
    f.writelines(['#!/bin/bash\n',
        '#file: '+opfile+':\n',
        '#SBATCH --job-name='+jobname+'\n',
        '#SBATCH --ntasks='+ntasks+'\n',
        '#SBATCH --nodes='+nodes+'\n',
        '#SBATCH --cpus-per-task='+cpus+'\n',
        '#SBATCH --mem='+mem+'\n',
        '#SBATCH --output='+logfile+'\n',
        'singularity exec '+container+' '+syscall+'\n',
        'sleep 10\n'])
    f.close()

    make_executable(opfile)


def generate_syscall_cubical(parset,myms,prefix):

    # Generate system call to run CubiCal

    now = timenow()
    outname = 'cube_'+prefix+'_'+myms.split('/')[-1]+'_'+now

    syscall = CUBICAL_EXEC+' '+parset+' '
    syscall += '--data-ms='+myms+' '
    syscall += '--out-name='+outname

    return syscall


def generate_syscall_tricolour(myms,datacol='DATA',fields=''):

    # Generate system call to run Tricolour 
    # -dc DATA_COLUMN, --data-column DATA_COLUMN
    #                       Name of visibility data column to flag (default: DATA)
    # -fn FIELD_NAMES, --field-names FIELD_NAMES
    #                       Name(s) of fields to flag. Defaults to flagging all
    #                       (default: [])

    syscall = 'source '+TRICOLOUR_VENV+' && '

    syscall += 'tricolour '
    syscall += '--data-column '+datacol+' '
    syscall += '--field-names '+fields+' '

    syscall += '&& deactivate'

    return syscall


def generate_syscall_wsclean(mslist,
                          imgname,datacol,
                          opfile,
                          imsize=8192,
                          cellsize='1.5asec',
                          briggs=-0.3,
                          niter=100000,
                          multiscale=False,
                          scales='0,5,15',
                          bda=False,
                          nomodel=False,
                          mask=False):

    # Generate system call to run wsclean

    syscall = 'wsclean '
    syscall += '-log-time '
    syscall += '-size '+str(imsize)+' '+str(imsize)+' '
    syscall += '-scale '+cellsize+' '
    if bda:
        syscall += '-baseline-averaging 24 '
        syscall += '-no-update-model-required '
    elif not bda and nomodel:
        syscall += '-no-update-model-required '
    if multiscale:
        syscall += '-multiscale '
        syscall += '-multiscale-scales '+scales+' '
    syscall += '-niter '+str(niter)+' '
    syscall += '-gain 0.1 '
    syscall += '-mgain 0.85 '
    syscall += '-weight briggs '+str(briggs)+' '
    syscall += '-datacolumn '+datacol+' '
    if mask:
        if mask == 'fits':
            mymask = glob.glob('*mask.fits')[0]
            syscall += '-fitsmask '+mymask+' '
        else:
            syscall += '-fitsmask '+mask+' '
    else:
        syscall += '-local-rms '
        syscall += '-auto-threshold 0.3 '
        syscall += '-auto-mask 5.5 '
    syscall += '-name '+imgname+' '
    syscall += '-channelsout 8 '
    syscall += '-fit-spectral-pol 4 '
    syscall += '-joinchannels '
    syscall += '-mem 90 '

    for myms in mslist:
        syscall += myms+' '

    return syscall


def generate_syscall_predict(msname,imgbase,opfile):

    # Generate system call to run wsclean in predict mode

    syscall = 'wsclean '
    syscall += '-log-time '
    syscall += '-predict '
    syscall += '-channelsout 8 '
    syscall += ' -size 8192 8192 '
    syscall += '-scale 1.5asec '
    syscall += '-name '+imgbase+' '
    syscall += '-mem 90 '
    syscall += '-predict-channels 64 '
    syscall += msname

    return syscall 


# ------------------------------------------------------------------------
