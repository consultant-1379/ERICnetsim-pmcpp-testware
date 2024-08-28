# /usr/bin/python

################################################################################
# COPYRIGHT Ericsson 2017
#
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
################################################################################

###################################################
# Version no    :  NSS 17.12
# Purpose       :  Script to support and trigger Genstats rollout
# Jira No       :  NSS-13234
# Gerrit Link   :  https://gerrit.ericsson.se/#/c/2494854/
# Description   :  Support nssModular Job, to exit and fail the job in case of ERRORs
# Date          :  07/06/2017
# Last Modified :  arwa.nawab@tcs.com
####################################################

'''
fabtasks is a script to rollout Genstats automatically

@author:     eaefhiq

@copyright:  2016 Ericsson. All rights reserved.

@license:    Ericsson

@contact:    liang.e.zhang@ericsson.com
'''

import logging
import sys
logging.basicConfig(filename="/tmp/genstats.log", level=logging.INFO)
from subprocess import Popen, PIPE
from StringIO import StringIO

RPM_PACKAGE = "ERICnetsimpmcpp_CXP9029065.rpm"
SIMULATION_DIR = "/netsim/netsim_dbdir/simdir/netsim/netsimdir/"
TMPFS_DIR = "/pms_tmpfs/"
MASTER_ROLLOUT_SCRIPT = "bash /netsim_users/pms/bin/pm_setup_stats_recordings.sh"
GENSTATS = "bash /netsim_users/pms/bin/genStats"
EUTRANCELL_DATA_FILE = "/netsim/genstats/eutrancellfdd_list.txt"
CHECK_DEPL_TYPE = "/netsim/simdepContents/"
PLAYBACK_CFG = "/netsim_users/pms/bin/playback_cfg"
SIM_DIR = "/netsim/netsim_dbdir/simdir/netsim/"
VFARM_TYPE_DIR = "/netsim/simdepContents/"
QA_LOG_FILE = "/netsim/genstats/logs/genstatsQA.log"

import os

def main(nssRelease="16.8", sim_data_list="",deplType="NSS"):
    sims = []
    mmes = []
    default_LTE_UETRACE_LIST = ["LTE01", "LTE02", "LTE03", "LTE04", "LTE05"]
    LTE_NE_map = {"LTE_UETRACE_LIST": [], "MSRBS_V1_LTE_UETRACE_LIST": [], "MSRBS_V2_LTE_UETRACE_LIST": [] }
    PM_file_paths = {}
    playback_sim_list = ""
    sim_data_list = get_sim_data()
    bsc_sim_list = []

    with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):

        for sim_info in sim_data_list :
             sim_data = sim_info.split()
             sim_name = sim_data[1]
             ne_type = sim_data[5]
             stats_dir = sim_data[9]
             trace_dir = sim_data[11]

             if ne_type not in PM_file_paths:
                if "PRBS" in ne_type and "RNC" not in sim_name:
                   PM_file_paths["MSRBS_V1"] = [stats_dir, trace_dir]
                elif "EPG" in ne_type:
                   PM_file_paths["EPG"] = [stats_dir, trace_dir]
                else:
                   PM_file_paths[ne_type] = [stats_dir, trace_dir]

             if "LTE" in sim_name:
                sim_ID = sim_name.split()[-1].split('-')[-1]
                if "LTE" in sim_ID and "TLS" not in sim_name:
                    sims.append(sim_ID)
                else:
                    sims.append(sim_name)
                if "PRBS" in ne_type or "MSRBS-V1" in ne_type:
                    LTE_NE_map["MSRBS_V1_LTE_UETRACE_LIST"].append(sim_ID)
                    if sim_ID in default_LTE_UETRACE_LIST:
                        default_LTE_UETRACE_LIST.remove(sim_ID)
                elif "MSRBS-V2" in ne_type:
                      LTE_NE_map["MSRBS_V2_LTE_UETRACE_LIST"].append(sim_ID)
                      if sim_ID in default_LTE_UETRACE_LIST:
                          default_LTE_UETRACE_LIST.remove(sim_ID)
             elif "RNC" in sim_name:
                  sims.append(sim_name.split()[-1].split('-')[-1])
             elif "SGSN" in sim_name:
                  mmes.append(sim_name.split()[-1])
             else:
                  sims.append(sim_name.split()[-1])

        if get_playback_list():
            for nes in get_playback_list():
                sim_list = []
                result = run("ls " + SIMULATION_DIR + " | grep {0}".format(nes))
                sim_list = result.split("\n")
                for sim_name in sim_list:
                    playback_sim_list = playback_sim_list + " " + sim_name.strip()
                    pm_stats_dir = run('python /netsim_users/pms/bin/getPMFileLocation.py --data_dir "fileLocation" --sim_name ' + sim_name +' --node_type '+ nes.upper())
                    pm_trace_dir = "/c/pm_data/"
                    PM_file_paths[nes] = [pm_stats_dir, pm_trace_dir]

        bsc_sim_list = get_bsc_list()
        if bsc_sim_list:
            for sim_name in bsc_sim_list:
                    sims.append(sim_name.strip())


    sims = list(set(sims))
    LTE_NE_map["LTE_UETRACE_LIST"] = default_LTE_UETRACE_LIST
    if deplType == "NSS":
        template = "netsim_cfg_template"
    elif deplType == "NRM3":
        template = "netsim_cfg_template_NRM3"
    elif deplType == "NRM1.2":
        template = "netsim_cfg_template_NRM1.2"
    create_netsim_cfg(
        get_hostname(), nssRelease, ' '.join(sims), ' '.join(mmes), PM_file_paths, playback_sim_list.strip(), template)
    put(get_hostname(), "/tmp")
    os.remove(get_hostname())
    
    
@task
def get_sim_data():
    env.user = "netsim"
    env.password = "netsim"
    run("python /netsim_users/auto_deploy/bin/getSimulationData.py")
    sim_data = run("cat /netsim/genstats/tmp/sim_data.txt")
    sim_data_list = filter(None, sim_data.split('\n'))
    return sim_data_list

