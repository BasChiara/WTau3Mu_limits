#! /usr/bin/env python

import os
import sys
import re
import time
import optparse
import datetime
import numpy as np
from itertools import product

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
import mva.config as config
import utils.combine_utils as Cutils


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


def setup_executable(exe_file, category, options, bdt_cut = 0.9800, quantile = 0.500, combination_cmd = None):
    
    # dump the text datacard
    with open(exe_file, 'w') as exe:
        exe.write(
    '''
#! /usr/bin/bash

WORK_DIR="{workdir}"
BASE_DIR="{basedir}/models/"
cd {workdir}

COMBINE_DIR="$WORK_DIR/input_combine"
CATEGORY="{cat}"

echo -e "\n"
echo    "|  CATEGORY $CATEGORY  |"
echo -e "\n"

{combination_command}

python3 $BASE_DIR/runBDTOptimCombine.py -i $COMBINE_DIR -d {full_tag} -n {full_tag} -M {method} -q {expQ} --BDTmin {bdt_min} --BDTmax {bdt_max} --BDTstep {bdt_step} -s limit
    '''.format(
        workdir = os.path.abspath(options.workdir),
        basedir = os.getcwd(),
        cat     = category,
        combination_command = combination_cmd if combination_cmd else '',
        full_tag= f'{options.process}_{category}{options.year}_{options.tag}',
        method  = options.Method,
        expQ    = quantile,
        bdt_min = bdt_cut,
        bdt_max = 1.0,
        bdt_step= 1.0,
    )
    )

    os.system(f'chmod +x {exe_file}')
    
    return

def setup_executable_singleDatacard(exe_file, datacard, options, bdt_cut = 0.9800, quantile = 0.500):
    
    # dump the text datacard
    with open(exe_file, 'w') as exe:
        exe.write(
    '''
#! /usr/bin/bash

WORK_DIR="{workdir}"
BASE_DIR="{basedir}/models/"
cd {workdir}

python3 $BASE_DIR/run_limitFromDatacard.py --input_datacard {datacard} -w $WORK_DIR -n .{full_tag} -s all -M {method} --CL 0.90 -q {expQ}

    '''.format(
        workdir = os.path.abspath(options.workdir),
        basedir = os.getcwd(),
        datacard= os.path.abspath(datacard),
        full_tag= options.tag,
        method  = options.Method,
        expQ    = quantile
    )
    )

    os.system(f'chmod +x {exe_file}')
    
    return

def write_src_file(src_file, exe_file, workdir):
    with open(src_file, 'w') as src:
            src.write(
            '''
#!/bin/bash\n
cd $COMBINEv10
cmsenv
cd {workdir}
echo $PWD\n
source {executable}
    '''.format(
        workdir = os.path.abspath(workdir),
        executable = os.path.basename(exe_file),
        )
            )
    

def main():
    
    ############# USAGE #############

    usage = '''usage: %prog [opts] dataset'''
    parser = optparse.OptionParser(usage=usage)

    # --defaults
    executable = 'to_calcUL'
    now = datetime.datetime.now()
    defaultoutputdir='jobs_report'

    # jobs params
    parser.add_option('-q', '--queue',       action='store',     dest='queue',        help='run in batch in queue specified as option (default -q 8nh)', default='8nh')
    parser.add_option('-n', '--nfileperjob', action='store',     dest='nfileperjob',  help='number of files processed by the single job'                , default=50,   type='int')
    parser.add_option('-p', '--prefix',      action='store',     dest='prefix',       help='the prefix to be added to the output'                      , default=defaultoutputdir)
    parser.add_option('-a', '--application', action='store',     dest='application',  help='the executable to be run'                                  , default=executable)
    parser.add_option('-c', '--create',      action='store_true',dest='create',       help='create only the jobs, do not submit them'                  , default=False)
    parser.add_option('-t', '--testnjobs',   action='store',     dest='testnjobs',    help='submit only the first n jobs'                              , default=1000000, type='int')
    parser.add_option('-r', '--runtime',     action='store',     dest='runtime',      help='New runtime for condor resubmission in hours. default None: will take the original one.', default=8, type=int)
    parser.add_option('--scheduler',         action='store',     dest='scheduler',    help='select the batch scheduler (lsf,condor). Default=condor'   , default='condor')
    # application params
    parser.add_option('-i','--input_datacard',dest='input_datacard',                        help='datacard to process',                                  default = None)
    parser.add_option('--process',           choices=['WTau3Mu', 'VTau3Mu'],                    dest='process',         help='which signature')
    parser.add_option('--workdir',           action='store',            dest='workdir',         help='copy the output datacard and .root in the specified path')
    parser.add_option('-M', '--Method',      choices=['AsymptoticLimits', 'HybridNew'],         dest='Method',         help='whcih combine method to use to calculate the limits',              default = 'AsymptoticLimits')
    parser.add_option('--tag',               action='store',            dest='tag',             help='tag that identifies the task')
    parser.add_option('--category',          choices=['A', 'B', 'C', 'ABC'],   dest='category', help='events category',                                         default = 'A')
    parser.add_option('--year',              choices=['22', '23', 'HL'],      dest='year',            help='data taking year',                                        default = '22')
    parser.add_option('--bdt_cut',           action='store',            dest='bdt_cut',         help='BDT value') 
    parser.add_option('--combine_cat',       action='store_true',       dest='combine_cat',           help='set to compute the combined limit also',                                        default = False)
    parser.add_option('--debug',             action='store_true',       dest='debug',           help='useful printouts',                                        default = False)
    (opt, args) = parser.parse_args()

    print("\n\n")

    ##### INPUT/OUTPUT #####
    job_tag = f'ULcalc{opt.Method}_20{opt.year}_{opt.tag}'

    # categories to process
    categories = []
    if (opt.category == 'ABC' and not opt.input_datacard):
        categories =['A', 'B', 'C']
    else : categories.append(opt.category)
    # --> setup the working directory
    if not os.path.isdir(opt.workdir):
        os.system(f'mkdir -p {opt.workdir}/input_combine')
        print(f'[+] working-directory created : {opt.workdir}')
    else:
        print(f'[+] working-directory aleardy exists : {opt.workdir}')
    
    # quantile points
    quantiles = [0.025, 0.160, 0.500, 0.840, 0.975] if opt.Method == 'HybridNew' else [0.500]

    # --> set-up the report directory
    jobdir = f'./{opt.prefix}/ULcalc_{opt.Method}_{opt.category}{opt.year}_{opt.tag}_'+ now.strftime("%Y%m%d_%H%M%S")
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
    jobs = list(product(categories, quantiles))
    srcfiles = []
    for i, job in enumerate(jobs):
        cat = job[0]
        quantile = job[1]

        
        # if datacard is provided use it
        if opt.input_datacard:
            executable_file_path = f'{opt.workdir}/{opt.application}_{opt.Method}_{opt.tag}_qExp{quantile}.sh'
            setup_executable_singleDatacard(
                executable_file_path, 
                datacard= opt.input_datacard,
                options= opt, 
                quantile = quantile)
        # else use my custom datacard convention
        else :
            # BDT cut value
            bdt_cut = opt.bdt_cut if opt.bdt_cut else config.wp_dict[opt.year][cat]

            # --> setup the executable
            executable_file_path = f'{opt.workdir}/{opt.application}_{opt.Method}_{cat}{opt.year}_qExp{quantile}.sh'
            setup_executable(executable_file_path, cat, opt, bdt_cut = bdt_cut, quantile = quantile)
        # --> setup the command sequence to run
        src_filename = f'{jobdir}/src/submit_{str(i)}.src'
        write_src_file(src_filename, executable_file_path, opt.workdir)
        if os.path.isfile(src_filename): srcfiles.append(src_filename)
        else: print(f'[ERROR] src file {src_filename} not created')

    # datacard combination
    if opt.combine_cat:
        
        datacard_list = [f'input_combine/datacard_{opt.process}_{cat}{opt.year}_{opt.tag}_bdt{opt.bdt_cut if opt.bdt_cut else config.wp_dict[opt.year][cat]:.4f}' for cat in categories]
        output = f'input_combine/datacard_{opt.process}_comb{opt.year}_{opt.tag}_bdt0.0000'
        combine_cmd = Cutils.combineCards_cmd(datacard_list, output, categories)
        print(f'[INFO] datacard combination command: {combine_cmd}')

        for q in quantiles:

            # --> setup the executable
            executable_file_path = f'{opt.workdir}/{opt.application}_{opt.Method}_comb{opt.year}_qExp{q}.sh'
            setup_executable(executable_file_path, 'comb', opt, bdt_cut=0.0,quantile=q, combination_cmd=combine_cmd)
            # --> setup the command sequence to run
            src_filename = f'{jobdir}/src/submit_comb_qExp{q}.src'
            write_src_file(src_filename, executable_file_path, opt.workdir)
            if os.path.isfile(src_filename): srcfiles.append(src_filename)
            else: print(f'[ERROR] src file {src_filename} not created')   
    
    
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
