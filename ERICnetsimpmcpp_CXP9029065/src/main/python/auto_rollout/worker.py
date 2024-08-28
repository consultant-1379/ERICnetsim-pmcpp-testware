from fabric.api import *
from fabric.operations import get
from fabric.contrib.files import exists
from StringIO import StringIO
from _collections import defaultdict

sim_info = '/netsim/genstats/tmp/sim_info.txt'
cronModificationScript = '/netsim_users/auto_deploy/bin/createNewCron.py'
selectiveNeScript = '/netsim_users/auto_deploy/bin/generateSelectiveNeConf.py'
GENSTATS_SCRIPT = '/netsim_users/pms/bin/genStats'
rpm_script = '/netsim_users/pms/bin/genStatsRPMVersion.sh'
PRODUCT_DATA_CFG='/netsim_users/reference_files/PmConfig_ENM/ProductDataSupportedDeployments/pd_deployment_id_cfg'

SUPPORTED_SELECTIVE_FLEX_NE_LIST = [ 'R6672', 'R6675', 'SPITFIRE']

fileSizeFinderScript = '/netsim_users/auto_deploy/bin/pmStatsFileSizeFinder.py'

PYTHON = 'python '

@task
def enable_selective_ne_flex_rop(sim_name, rop, ne_count):
    env.user = 'netsim'
    env.password = 'netsim'
    passed_ne_sim_map = defaultdict(list)
    sim_info_list = []
    rpm_version_full_string = run('bash ' + rpm_script)
    rpm_number_version_string = rpm_version_full_string.split("-")[1]
    rmp_integer = int(rpm_number_version_string.replace(".", ""))
    print "RPM Version " + rpm_number_version_string
    
    if exists(sim_info, use_sudo=False):
        sim_info_io = StringIO()
        get(sim_info, sim_info_io)
        sim_info_data = sim_info_io.getvalue()
        sim_info_list = filter(None, sim_info_data.split('\n'))
        if sim_info_list:
            sim_name_list = list(set(sim_name.split('|')))
            for sim in sim_name_list:
                for line in sim_info_list:
                    lineElements = line.split(':')
                    if sim == lineElements[0]:
                        if lineElements[1] in SUPPORTED_SELECTIVE_FLEX_NE_LIST:
                            passed_ne_sim_map[lineElements[1]].append(sim)
                        break
            if passed_ne_sim_map:
                if rmp_integer < 20402:
                    run('python ' + cronModificationScript + ' -r ' + rop + ' -l "' + ':'.join(passed_ne_sim_map.keys()) + '" -c ' \
                        + GENSTATS_SCRIPT + ' -t ADD')
                    for ne, sim_list in passed_ne_sim_map.iteritems():
                        for sim in sim_list:
                            run('python ' + selectiveNeScript + ' --sim ' + sim + ' --rop ' + rop + ' --count ' + ne_count )
                else:
                    if rop == "1":
                        print 'ERROR: This job is expected to fail with releases 22.11 and above(or with RPM versions 2.0.402 and above) with 1 min ROP for R6672, R6675 and SPITFIRE nodes as there is no more requirement to support 1 min flex ROP via this module for these node types. 1 min ROP is added by default to Genstats for R66 family and SPITFIRE nodes. In case you want the old support then rollout Genstats with versions 22.10 or below and then run this module. Further details can be found in NSS-35621 and NSS-40482.'
            else:
                print 'ERROR: There are only 3 supported nodeypes R6672, R6675 and SPITFIRE. None of the 3 were found active on the deployed VM'
        else:
            print sim_info + ' file does not have any data. Can not enable Selective NE PM Generation.'
    else:
        print sim_info + ' file does not exists. Can not enable Selective NE PM Generation.'


@with_settings(warn_only=True)
@task
def find_stats_file_size(master, serverList, checkLatestRopFile):
    env.user = 'netsim'
    env.password = 'netsim'

    if not exists(fileSizeFinderScript, use_sudo=False):
        print "ERROR : script " + fileSizeFinderScript + " is not present."
    else:
        if checkLatestRopFile == "true":
            run( PYTHON + fileSizeFinderScript + ' --checkLatestRopFileSize YES' + ' --master "' + master + '" --servers "' + serverList + '"' )
        else:
            run( PYTHON + fileSizeFinderScript + ' --checkLatestRopFileSize NO' + ' --master "' + master + '" --servers "' + serverList + '"' )
            
            
@task
def enable_product_data_support():
    """
        This function will update the product data cfg file to NO to YES and YES to NO
    """
    env.user = "netsim"
    env.password = "netsim" 
    
    if not exists(PRODUCT_DATA_CFG, use_sudo=False):
        print "ERROR : file " + PRODUCT_DATA_CFG + " is not present."
    else:
        # Check if "NO" is present in the cfg file
        is_no = run("grep -Eo 'GENERATE_PD_FILES=\"([^\"]+)\"' {} | cut -d'\"' -f2".format(PRODUCT_DATA_CFG))
    
        if is_no == "NO":
            # Change "NO" to "YES"
            run("sed -i 's/GENERATE_PD_FILES=.*/GENERATE_PD_FILES=\"YES\"/' {}".format(PRODUCT_DATA_CFG))
        else:
            # Change "YES" to "NO"
            run("sed -i 's/GENERATE_PD_FILES=.*/GENERATE_PD_FILES=\"NO\"/' {}".format(PRODUCT_DATA_CFG))