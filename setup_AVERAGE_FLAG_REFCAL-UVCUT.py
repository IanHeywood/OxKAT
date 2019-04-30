#!/usr/bin/env python
# ianh@astro.ox.ac.uk


import sys
import glob
from oxkat import generate_jobs as gen


def main():


    CWD = gen.CWD
    OXKAT = gen.OXKAT
    SCRIPTS = gen.SCRIPTS
    LOGS = gen.LOGS
    PARSETS = gen.PARSETS
    CASA_CONTAINER = gen.CASA_CONTAINER
    WSCLEAN_CONTAINER = gen.WSCLEAN_CONTAINER
    CUBICAL_CONTAINER = gen.CUBICAL_CONTAINER
    

    submit_file = sys.argv[1]


    gen.setup_scripts_dir()


    f = open(submit_file,'w')


    myms = glob.glob('*.ms')[0]
    code = gen.get_code(myms)
    myms = myms.replace('.ms','_wtspec.ms')


    cmd = 'casa -c '+OXKAT+'/01_casa_average_to_1k.py --nologger --log2term --nogui'
    slurmfile = SCRIPTS+'/slurm_avg_'+code+'.sh'
    logfile = slurmfile.replace('.sh','.log')
    job_id_avg = 'AVG_'+code
    gen.write_slurm(code+'avrg',logfile,CASA_CONTAINER,cmd,slurmfile)


    syscall = job_id_avg+"=`sbatch "
    syscall += slurmfile+" | awk '{print $4}'`"
    f.write(syscall+'\n')


    cmd = 'python '+OXKAT+'/00_setup.py '+myms
    slurmfile = SCRIPTS+'/slurm_info_'+code+'.sh'
    logfile = slurmfile.replace('.sh','.log')
    job_id_info = 'INFO_'+code
    gen.write_slurm(code+'info',logfile,CUBICAL_CONTAINER,cmd,slurmfile)


    syscall = job_id_info+"=`sbatch "
    syscall += "-d afterok:${"+job_id_avg+"} "
    syscall += slurmfile+" | awk '{print $4}'`"
    f.write(syscall+'\n')


    cmd = 'casa -c '+OXKAT+'/01_casa_hardmask_and_flag.py --nologger --log2term --nogui'
    slurmfile = SCRIPTS+'/slurm_flag_'+code+'.sh'
    logfile = slurmfile.replace('.sh','.log')
    job_id_flag = 'FLAG_'+code
    gen.write_slurm(code+'flag',logfile,CASA_CONTAINER,cmd,slurmfile)


    syscall = job_id_flag+"=`sbatch "
    syscall += "-d afterok:${"+job_id_info+"} "
    syscall += slurmfile+" | awk '{print $4}'`"
    f.write(syscall+'\n')


    cmd = 'casa -c '+OXKAT+'/casa_refcal_uvcut.py --nologger --log2term --nogui'
    slurmfile = SCRIPTS+'/slurm_refcal_'+code+'.sh'
    logfile = slurmfile.replace('.sh','.log')
    job_id_refcal = 'REFCAL_'+code
    gen.write_slurm(code+'rcal',logfile,CASA_CONTAINER,cmd,slurmfile)


    syscall = job_id_refcal+"=`sbatch "
    syscall += "-d afterok:${"+job_id_flag+"} "
    syscall += slurmfile+" | awk '{print $4}'`"
    f.write(syscall+'\n')


    f.close()


if __name__ == "__main__":


    main()
