import ROOT
import os 
import re
import time
import optparse
import datetime
import itertools
import numpy as np
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import mva.config as config

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

def write_src_file(filename, r_gen, fit_f, gen_f, cat, options):
    src_file = open(filename, 'w')
    src_file.write('''
cd {workdir}
python3 {exe} --do_fit_step --do_pull_step --Ntoys {nToys} --Nfit {nFit} --r_gen_list {r_gen:.1f} --gen_func_list {gFunc} --fit_func_list {fFunc} --year {year} --tag {tag} --category {category}
'''.format(
        workdir = os.path.abspath(options.workdir),
        exe     = options.application,
        nToys   = options.nToys,
        nFit    = options.nFit,
        r_gen   = r_gen,
        gFunc   = gen_f,
        fFunc   = fit_f,
        year    = options.year,
        tag     = options.tag,
        category= cat
        )
    )
    src_file.close()
    return filename


def main():
    
    ############# USAGE #############

    usage = '''usage: %prog [opts] dataset'''
    parser = optparse.OptionParser(usage=usage)

    # --defaults
    executable = 'BiasSignal_wrapper.py'
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
    parser.add_option('--workdir',           action='store',            dest='workdir',         help='copy the output datacard and .root in the specified path')
    parser.add_option('--tag',               action='store',            dest='tag',             help='tag that identifies the task')
    parser.add_option('--plot_outdir',       action='store',            dest='plot_outdir',             help='copy the output plot in the specified EOS path',          default = '')
    parser.add_option('--category',          choices=['A', 'B', 'C', 'ABC', 'comb'],   dest='category',        help='events category',                                         default = 'A')
    parser.add_option('--year',              choices=['22', '23'],      dest='year',            help='data taking year',                                        default = '22')
    parser.add_option('--nToys',             action='store',            dest='nToys',           help='number of gen toys',                                      default = 50000, type='int')  
    parser.add_option('--nFit',              action='store',            dest='nFit',            help='number of toys to fit',                                   default = 50000, type='int')  
    parser.add_option('--debug',             action='store_true',       dest='debug',           help='useful printouts',                                        default = False)
    (opt, args) = parser.parse_args()

    print("\n\n")

    ##### INPUT/OUTPUT #####
    job_tag = f'FitBiasCombine_20{opt.year}{opt.category}_{opt.tag}'
    categories = []
    if opt.category == 'ABC':
        categories =['A', 'B', 'C']
    else : categories.append(opt.category)
    # --> setup the working directory
    if not os.path.isdir(opt.workdir):
        os.system(f'mkdir -p {opt.workdir}/fit_results')
        #os.system(f'mkdir -p {opt.workdir}/src')
        print(f'[+] working-directory created : {opt.workdir}')
    else:
        print(f'[+] working-directory aleardy exists : {opt.workdir}')



    # --> set-up the report directory
    jobdir = f'./{opt.prefix}/FitBiasCombine_{opt.category}20{opt.year}_{opt.tag}_'+ now.strftime("%Y%m%d_%H%M%S")
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

    # set-up
    functions = ['expo', 'const']#, 'poly1']
    wp_dict   = config.wp_dict[opt.year]

    srcfiles = []
    i = 0
    for cat in categories:
        
        print(f'[+] Category {cat}')
        r_gen_list    = [0.0, config.sensitivity_dict[opt.year][cat], 3*config.sensitivity_dict[opt.year][cat]]
        if opt.category == 'comb':
            r_gen_list.append(10*config.sensitivity_dict[opt.year][cat])
        for r_gen in r_gen_list:
            for func_pair in list(itertools.product(functions, repeat=2)):
                gen_f, fit_f = func_pair[0], func_pair[1]
                print(f' - gen_func = {gen_f} fit_func = {fit_f} with signal strength r = {r_gen:.1f}')

                src_filename = f'{jobdir}/src/submit_{str(i)}.src'
                #def write_src_file(filename, r_gen, fit_f, gen_f, cat, options):
                write_src_file(src_filename, r_gen, fit_f, gen_f, cat, opt)
                srcfiles.append(src_filename)
                i += 1

    ##### JOB SUBMISSION #####
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


