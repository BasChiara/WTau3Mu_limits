#! /usr/bin/env python

import os
import sys
import re
import time
import optparse
import datetime
import numpy as np


def makeCondorFile(jobdir, srcFiles, batch_name, options):
    dummy_exec = open(jobdir+'/dummy_exec.sh','w')
    dummy_exec.write('#!/bin/bash\n')
    dummy_exec.write('bash $*\n')
    dummy_exec.close()

    condor_file_name = jobdir+'/condor_submit.condor'
    condor_file = open(condor_file_name,'w')
    condor_file.write('''
universe = vanilla
executable = {de}
use_x509userproxy = true

log        = {jd}/log/$(ProcId).log
output     = {jd}/out/$(ProcId).out
error      = {jd}/out/$(ProcId).error

getenv       = True
environment  = "LS_SUBCWD={here}"

request_memory = 5M 
+MaxRuntime = {rt}\n
+JobBatchName = "{bn}"\n
'''.format(de=os.path.abspath(dummy_exec.name), jd=os.path.abspath(jobdir), rt=int(options.runtime*3600), bn=batch_name,here=os.environ['PWD'] ) )

    for sf in srcFiles:
        condor_file.write('arguments = {sf} \nqueue 1 \n\n'.format(sf=os.path.abspath(sf)))

    condor_file.close()
    return condor_file_name

def zip_jobScripts(options):

    fit_script = "/afs/cern.ch/user/c/cbasile/WTau3MuRun3_Analysis/CMSSW_13_0_13/src/Tau3MuAnalysis/models/Tau3Mu_fitSB.py"
    pwd =  os.getcwd()
    print(f'[INFO] current path is {pwd}') 
    opt_script = pwd + "/models/runBDTOptimCombine.py"
    plt_script = pwd + "/models/compareLimitScan.py"

    # zip the scripts
    print(f'[...] compressing the scripts')
    tar_ball_name = f'{options.workdir}/scripts.tar.gz'
    if not os.path.exists(tar_ball_name):
        os.system(f'cp {fit_script} {opt_script} {plt_script} .')
        os.system(f'tar -czvf {tar_ball_name} {os.path.basename(fit_script)} {os.path.basename(opt_script)} {os.path.basename(plt_script)}')
        if os.path.exists(tar_ball_name):
            print(f'   OK - tarball created : {tar_ball_name}')
            os.system(f'rm {os.path.basename(fit_script)} {os.path.basename(opt_script)} {os.path.basename(plt_script)}')
        else:
            print(f'[ERROR] problem in creating tarball {tar_ball_name}')
            exit()
    else:
        print('  tarball with scripts already in workdir')
    
    return tar_ball_name


def setup_executable(exe_file, tar_scripts, category, options):

    # dump the text datacard
    with open(exe_file, 'w') as exe:
        exe.write(
    '''
#! /usr/bin/bash

WORK_DIR="{workdir}"
BASE_DIR="{basedir}/models/"
cd {workdir}
#tar -xvzf {scripts} -C $BASE_DIR

TAG="{tag}"

COMBINE_DIR="$WORK_DIR/input_combine"

EOS_DIR="{eos}"
YEAR="{year}"
SIGNAL="{signal}"
DATA="{data}"

CATEGORY="{cat}"

echo -e "\n"
echo    "|  CATEGORY $CATEGORY  |"
echo -e "\n"
echo 'TIME TO FIT'
python3 $BASE_DIR/Tau3Mu_fitSB.py --plot_outdir $EOS_DIR --combine_dir $COMBINE_DIR -s $SIGNAL -d $DATA --category $CATEGORY -y $YEAR --tag $TAG --optim_bdt --save_ws --bkg_func dynamic --BDTmin 0.9900 --BDTmax 0.9995 --BDTstep 0.0005
echo 'TIME TO CALCULATE LIMITS'
# with AsymptoticLimits
python3 $BASE_DIR/runBDTOptimCombine.py -i $COMBINE_DIR -o $EOS_DIR --scan_sensitivity input_combine/sensitivity_tree_bdt_scan_{full_tag}.root -d {full_tag} -n {full_tag} --BDTmin 0.9900 --BDTmax 0.9995 --BDTstep 0.0005 -s all
# with HybridNew 
python3 $BASE_DIR/runBDTOptimCombine.py -i $COMBINE_DIR -o $EOS_DIR --scan_sensitivity input_combine/sensitivity_tree_bdt_scan_WTau3Mu_{full_tag}.root -d {full_tag} -n {full_tag} -M HybridNew --BDTmin 0.9900 --BDTmax 0.9995 --BDTstep 0.0005 -s all
echo 'TIME TO COMPARE THE METHODS'
# compare the methods
python3 $BASE_DIR/compareLimitScan.py --inputs input_combine/Tau3MuCombine.{full_tag}_BDTscan.AsymptoticLimits.root --labels AsymptoticLimits --inputs input_combine/Tau3MuCombine.{full_tag}_BDTscan.HybridNew.root --labels HybridNew -o $EOS_DIR -d {full_tag} -n {full_tag} -y 20$YEAR -c $CATEGORY
    '''.format(
        workdir = os.path.abspath(options.workdir),
        basedir = os.getcwd(),
        scripts = tar_scripts,
        tag     = options.tag,
        eos     = options.plot_outdir,
        year    = options.year,
        signal  = options.signal,
        data    = options.data,
        cat     = category,
        full_tag= f'WTau3Mu_{category}{options.year}_{options.tag}'
    )
    )

    os.system(f'chmod +x {exe_file}')
    
    return
    

    

def main():
    
    ############# USAGE #############

    usage = '''usage: %prog [opts] dataset'''
    parser = optparse.OptionParser(usage=usage)

    # --defaults
    executable = 'to_run_fit_and_limits_condor'
    now = datetime.datetime.now()
    defaultoutputdir='jobs_report'

    # jobs params
    parser.add_option('-q', '--queue',       action='store',     dest='queue',        help='run in batch in queue specified as option (default -q 8nh)', default='8nh')
    parser.add_option('-n', '--nfileperjob', action='store',     dest='nfileperjob',  help='number of files processed by the single job'                , default=50,   type='int')
    parser.add_option('-p', '--prefix',      action='store',     dest='prefix',       help='the prefix to be added to the output'                      , default=defaultoutputdir)
    parser.add_option('-a', '--application', action='store',     dest='application',  help='the executable to be run'                                  , default=executable)
    parser.add_option('-c', '--create',      action='store_true',dest='create',       help='create only the jobs, do not submit them'                  , default=False)
    parser.add_option('-t', '--testnjobs',   action='store',     dest='testnjobs',    help='submit only the first n jobs'                              , default=1000000, type='int')
    #parser.add_option('-N', '--neventsjob',  action='store',     dest='neventsjob',   help='split the jobs with n events  / batch job'                 , default=200,   type='int')
    #parser.add_option('-T', '--eventsperfile',action='store',    dest='eventsperfile',help='number of events per input file'                        , default=-1,   type='int')
    parser.add_option('-r', '--runtime',     action='store',     dest='runtime',      help='New runtime for condor resubmission in hours. default None: will take the original one.', default=8, type=int)
    parser.add_option('--scheduler',         action='store',     dest='scheduler',    help='select the batch scheduler (lsf,condor). Default=condor'   , default='condor')
    # application params
    parser.add_option('-s','--signal',       action='store',            dest='signal',          help='signal sample')
    parser.add_option('-d','--data',         action='store',            dest='data',            help='data sample')
    parser.add_option('--workdir',           action='store',            dest='workdir',         help='copy the output datacard and .root in the specified path')
    parser.add_option('--tag',               action='store',            dest='tag',             help='tag that identifies the task')
    parser.add_option('--plot_outdir',       action='store',            dest='plot_outdir',             help='copy the output plot in the specified EOS path',          default = '')
    parser.add_option('--category',          choices=['A', 'B', 'C', 'ABC'],   dest='category',        help='events category',                                         default = 'A')
    parser.add_option('--year',              choices=['22', '23'],      dest='year',            help='data taking year',                                        default = '22')
    parser.add_option('--debug',             action='store_true',       dest='debug',           help='useful printouts',                                        default = False)
    (opt, args) = parser.parse_args()

    print("\n\n")

    ##### INPUT/OUTPUT #####
    job_tag = f'BDTopt_20{opt.year}_{opt.tag}'
    categories = []
    if opt.category == 'ABC':
        categories =['A', 'B', 'C']
    else : categories.append(opt.category)
    # --> setup the working directory
    if not os.path.isdir(opt.workdir):
        os.system(f'mkdir -p {opt.workdir}/input_combine')
        #os.system(f'mkdir -p {opt.workdir}/src')
        print(f'[+] working-directory created : {opt.workdir}')
    else:
        print(f'[+] working-directory aleardy exists : {opt.workdir}')
    # --> tarball with scripts to run
    scripts = zip_jobScripts(opt)
    # --> setup the ouput directory
    if not os.path.isdir(opt.plot_outdir):
        os.system(f'mkdir -p {opt.plot_outdir}')
        os.system(f'cp ~/public/index.php {opt.plot_outdir}')
        print(f'[+] plot-directory created : {opt.plot_outdir}')
    else:
        print(f'[+] plot-directory already exists : {opt.plot_outdir}')

    # --> set-up the report directory
    jobdir = f'./{opt.prefix}/BDToptimization_{opt.category}{opt.year}_{opt.tag}_'+ now.strftime("%Y%m%d_%H%M%S")
    os.system("mkdir -p "+jobdir)
    os.system("mkdir -p "+jobdir+"/log/")
    os.system("mkdir -p "+jobdir+"/out/")
    os.system("mkdir -p "+jobdir+"/src/")
    os.system("mkdir -p "+jobdir+"/cfg/")
    print('[LOG] report will be saved in '+ jobdir)

    #look for the current directory
    #######################################
    pwd = os.environ['PWD']
    scramarch = os.environ['SCRAM_ARCH']
    #######################################

    srcfiles = []
    for i, cat in enumerate(categories):
    
        # --> setup the executable
        executable_file_path = f'{opt.workdir}/{opt.application}_{cat}.sh'
        setup_executable(executable_file_path, scripts, cat, opt)
        # --> setup the command sequence to run
        src_filename = f'{jobdir}/src/submit_{str(i)}.src'
        with open(src_filename, 'w') as src:
            src.write(
            '''
#!/bin/bash\n
cd $COMBINEv10 
cmsenv
cd {workdir}
echo $PWD\n
source {executable}
    '''.format(
        workdir = opt.workdir,
        executable = os.path.basename(executable_file_path),
        )
            )
        srcfiles.append(src_filename)

   
    #######################################

    if opt.scheduler=='condor':
        cf = makeCondorFile(jobdir, srcfiles, job_tag, opt)
        subcmd = 'condor_submit {rf} '.format(rf = cf) #lunch jobs
        if opt.create:
            print('running dry, printing the commands...')
            print(subcmd)
        else:
            print('submitting for real...')
            os.system(subcmd)

if __name__ == "__main__":
        main()
