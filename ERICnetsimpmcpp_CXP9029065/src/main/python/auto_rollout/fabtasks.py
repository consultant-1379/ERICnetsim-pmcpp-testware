# /usr/bin/python

################################################################################
# COPYRIGHT Ericsson 2023
#
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
################################################################################

####################################################
# Version no    :  NSS 24.07
# Purpose       :  Script to support and trigger Genstats rollout
# Jira No       :  NSS-NSS-47713
# Gerrit Link   :  https://gerrit.ericsson.se/#/c/17553134/
# Description   :  Genstats support to create Small NRM6.2.1 with 12 CBRS devices for SADC in CDL
# Date          :  07/03/2024
# Last Modified :  g.shashikumar@tcs.com
####################################################

'''
fabtasks is a script to rollout Genstats automatically

@author:     eaefhiq

@copyright:  2021 Ericsson. All rights reserved.

@license:    Ericsson

@contact:    liang.e.zhang@ericsson.com
'''

import logging
import sys
import os
from fabric.api import *
from fabric.operations import put
from fabric.operations import get
logging.basicConfig(filename="/tmp/genstats.log", level=logging.INFO)
from subprocess import Popen, PIPE
from StringIO import StringIO

RPM_PACKAGE = "ERICnetsimpmcpp_CXP9029065.rpm"
SIMULATION_DIR = "/netsim/netsim_dbdir/simdir/netsim/netsimdir/"
TMPFS_DIR = "/pms_tmpfs/"
MASTER_ROLLOUT_SCRIPT = "bash /netsim_users/pms/bin/pm_setup_stats_recordings.sh"
GENSTATS = "bash /netsim_users/pms/bin/genStats"
EUTRANCELL_DATA_FILE = "/netsim/genstats/eutrancellfdd_list.txt"
NRM_DETAILS_FILE = '/netsim/simdepContents/NRMDetails'
PLAYBACK_CFG = "/netsim_users/pms/bin/playback_cfg"
SIM_DIR = "/netsim/netsim_dbdir/simdir/netsim/"
VFARM_TYPE_DIR = "/netsim/simdepContents/"
QA_LOG_FILE = "/netsim/genstats/logs/genstatsQA.log"
SIM_DATA_FILE = "/netsim/genstats/tmp/sim_data.txt"
LOGS_DIR = "/netsim/genstats/logs/"
SGSN_REAL_DATA = "/real_data/HSTNTX01LT9/"
INSTALL_STUB_OSS_LOGS = "/netsim_users/pms/logs/netsim_stub_logs/installation.log"
PATCHING_SCRIPT = "/netsim_users/pms/bin/bandwidthPatch.py"
BANDWIDTH_SCRIPT = "./patch/bandwidthPatch.py"
NETSIM_RHOSTS_FILE = "/netsim/.rhosts"
ROLLOUT_LOG_FILE = "/tmp/genstats_rollout.log"
RADIO_NODE_NE = ["VTFRADIONODE", "5GRADIONODE", "TLS", "VRM", "VRSM","VSAPC", "VTIF", "PCC", "PCG", "CCSM", "CCDM", "CCRC", "CCPC", "SC", "CCES"]
EDE_SUPPORTED_TRANSPORT_SIM_LIST = ['FrontHaul']
SUPPORTED_AUTO_DETECT_NRM_DEPLOYMENTS = [ 'NRM' + x for x in [ '3', '4', '4.1', '5', '5.1', '6', '6.1', '6.2', '6.2.1', '6.3', '6.4', '7']]
SUPPORTED_AUTO_DETECT_NEE_DEPLOYMENTS = ['MD_' + y for y in ['1']]
SUPPORTED_AUTO_DETECT_DO_DEPLOYMENTS = ['DO']
SUPPORTED_AUTO_DETECT_DEPLOYMENTS = SUPPORTED_AUTO_DETECT_NRM_DEPLOYMENTS + SUPPORTED_AUTO_DETECT_NEE_DEPLOYMENTS + SUPPORTED_AUTO_DETECT_DO_DEPLOYMENTS

from netsim_cfg_gen import *
import os

def upload_cfg(nssRelease, sim_data_list,edeStatsCheck,deplType="NSS",counterVolume="None",oss_enabled="False"):
    sims = []
    mmes = []
    default_LTE_UETRACE_LIST = ["LTE01", "LTE02", "LTE03", "LTE04", "LTE05"]
    LTE_NE_map = {"LTE_UETRACE_LIST": [], "MSRBS_V1_LTE_UETRACE_LIST": [], "MSRBS_V2_LTE_UETRACE_LIST": [] }
    PM_file_paths = {}
    playback_sim_list = ""
    bsc_sim_list = []
    msc_sim_list = []
    hlr_sim_list = []
    ecs_sim_list = []

    with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):

        for sim_info in sim_data_list :
             sim_data = sim_info.split()
             sim_name = sim_data[1]
             ne_type = sim_data[5]
             stats_dir = sim_data[9]
             trace_dir = sim_data[11]
             pd_dir = sim_data[13]

             if ne_type == 'PRBS' and 'LTE' in sim_name:
                 ne_type = 'MSRBS_V1'

             if ne_type not in PM_file_paths:
                if "EPG" in ne_type:
                   PM_file_paths["EPG"] = [stats_dir, trace_dir, pd_dir]
                elif "5GRADIONODE" in ne_type:
                   PM_file_paths["FIVEGRADIONODE"] = [stats_dir, trace_dir, pd_dir]
                else:
                   PM_file_paths[ne_type] = [stats_dir, trace_dir, pd_dir]
             if "LTE" in sim_name:
                sim_ID = sim_name.split()[-1].split('-')[-1]
                if any(radio_ne in sim_name.upper() for radio_ne in RADIO_NODE_NE):
                   sims.append(sim_name)
                else:
                   sims.append(sim_ID)
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
             elif "FRONTHAUL" in sim_name.upper():
                  if edeStatsCheck:
                      sims.append(sim_name.split()[-1])
             else:
                  sims.append(sim_name.split()[-1])

        if get_playback_list(edeStatsCheck):
            sim_list = []
            for nes in get_playback_list(edeStatsCheck):
                result = run("ls " + SIMULATION_DIR + " | grep -v .zip | egrep -v 'MSC|HLR'" + " | grep {0}".format(nes))
                sim_list += result.split("\n")
                sim_list = [sim for sim in sim_list if "6392" not in sim]
            sim_list = list(set(sim_list))
            for sim_name in sim_list:
                playback_sim_list = playback_sim_list + " " + sim_name.strip()

        bsc_sim_list = get_bsc_list()
        if bsc_sim_list:
            for sim_name in bsc_sim_list:
                    sims.append(sim_name.strip())

        msc_sim_list = get_msc_list()
        if msc_sim_list:
            for sim_name in msc_sim_list:
                sims.append(sim_name.strip())

        hlr_sim_list = get_hlr_list()
        if hlr_sim_list:
            for sim_name in hlr_sim_list:
                sims.append(sim_name.strip())

        ecs_sim_list = get_ecs_list()
        if ecs_sim_list:
            for sim_name in ecs_sim_list:
                sims.append(sim_name.strip())

    sims = list(set(sims))
    LTE_NE_map["LTE_UETRACE_LIST"] = default_LTE_UETRACE_LIST
    template = "netsim_cfg_template_omni"
    if deplType == "NSS" and oss_enabled == "True":
        template = "netsim_cfg_OSS"
    create_netsim_cfg(
        get_hostname(), nssRelease, ' '.join(sims), ' '.join(mmes), PM_file_paths, playback_sim_list.strip(), template, edeStatsCheck, counterVolume, oss_enabled, deplType)
    put(get_hostname(), "/tmp")
    os.remove(get_hostname())


def get_hostname():
    netsim_cfg_file = run("hostname") 
    if "atvts" in netsim_cfg_file:
        netsim_cfg_file = "netsim"
    return netsim_cfg_file


def rollout_genstats(oss_bulk_pm_enabled="False"):
    run(MASTER_ROLLOUT_SCRIPT + " -c /tmp/" + get_hostname() + " -b " + oss_bulk_pm_enabled)

def rollout_edeStats():
    env.user = "netsim"
    env.password = "netsim"
    run('/EDE_Stats_CXP9034659/EDE_Stats_CXP9034659/bin/generate_xml.bsh -r "15:ALL"')
    run("python /EDE_Stats_CXP9034659/EDE_Stats_CXP9034659/bin/EDEStats.py")

# Added with an intention to troubleshoot RV issues
@task
def run_genstats():
    env.user = "netsim"
    env.password = "netsim"
    run(GENSTATS)


@task
def apply_existing_cfg():
    env.user = "netsim"
    env.password = "netsim"
    print "INFO: reapplying existing /netsim/netsim_cfg configuration"
    run(MASTER_ROLLOUT_SCRIPT + " -c /netsim/netsim_cfg")

def upload_rhosts():
    run("rm -f " + ROLLOUT_LOG_FILE)
    if exists(NETSIM_RHOSTS_FILE, use_sudo=False):
        file_permission = run("stat -c %a " + NETSIM_RHOSTS_FILE)
        if not file_permission == '644':
            run( 'echo "WARNING : Permission for ' + NETSIM_RHOSTS_FILE + ' file is ' + file_permission + ' instead of 644." >> ' +ROLLOUT_LOG_FILE )
            run('echo "INFO: Changing  permission of  ' + NETSIM_RHOSTS_FILE + ' to ' +file_permission+ ' permission" >> ' +ROLLOUT_LOG_FILE)
            run("chmod 644 " + NETSIM_RHOSTS_FILE)
    else:
        print "INFO: copying " + NETSIM_RHOSTS_FILE + " file."
        put(".rhosts", "~/")


def upload_rpm():
    put(RPM_PACKAGE, "/tmp")


def remove_not_started_node_directory():
    env.user = "root"
    env.password = "shroot"
    run("bash /netsim_users/pms/bin/remove_stop_nodes.sh")

def download_rpm(rpm_version="RELEASE"):
    run("curl -L \"" + rpm_version + "\" -o /tmp/ERICnetsimpmcpp_CXP9029065.rpm")

@task
def install_rpm(rpm_version):
    env.warn_only = True
    download_rpm(rpm_version)
    run("rm -rf /netsim_users/*")
    run("rpm -Uvh --force /tmp/" + RPM_PACKAGE)
    run("chown netsim:netsim /netsim_users/ -R")
    run("rm /tmp/" + RPM_PACKAGE)
    run("chown -R netsim:netsim /pms_tmpfs/")


@task
def root_run(rpm_version):
    env.user = "root"
    env.password = "shroot"
    install_rpm(rpm_version)

def install_netsim_stub_OSS(deplType, nodeMOMVer, nwXMLpath):
    env.user = "root"
    env.password = "shroot"
    run("curl -L \"https://arm901-eiffel004.athtem.eei.ericsson.se:8443/nexus/content/repositories/nss-releases/com/ericsson/nss/Genstats/NodeMOMs/" + nodeMOMVer + "/NodeMOMs-" + nodeMOMVer + ".zip\" -o /tmp/NodeMOMs.zip")
    run("bash /netsim_users/netsim_stub/install.sh -d "  +deplType+ " -n " + nwXMLpath)
    if exists(INSTALL_STUB_OSS_LOGS, use_sudo=False):
       fd = StringIO()
       get(INSTALL_STUB_OSS_LOGS, fd)
       install_stub_oss_logs=fd.getvalue()
       install_stub_oss_logs_list = filter(None, install_stub_oss_logs.split('\n'))
       for line in install_stub_oss_logs_list:
           if 'error' in line.lower():
               print "ERROR :Installation of netsim_stub failed. Exiting from OSS_PM tool rollout"
               sys.exit(1)
    else:
         print "Log File " + INSTALL_STUB_OSS_LOGS + " does not exist"
         sys.exit(1)

@task
def edeStatsRollOut(edeStats_rollout_version):
    env.user = "root"
    env.password = "shroot"
    install_edeStats(edeStats_rollout_version)

@task
def bandwidthPatch(**opts):
    env.user = "netsim"
    env.password = "netsim"
    options = " "
    for key,value in opts.iteritems():
        options = options + key + "=" + value + " "
    put(BANDWIDTH_SCRIPT, "/netsim_users/pms/bin/")
    run ("chmod 775 " + PATCHING_SCRIPT)
    run(PATCHING_SCRIPT + options)

@task
def runlimitBW():
    env.user = "root"
    env.password = "shroot"
    run("bash /netsim_users/pms/bin/limitbw -n -c > /netsim_users/pms/logs/limitbw.log")
    run("bash /netsim_users/pms/bin/limitbw -n -g >> /netsim_users/pms/logs/limitbw.log")

@task
def install_edeStats(edeStats_rollout_version):
    #run("curl -L \"https://arm901-eiffel004.athtem.eei.ericsson.se:8443/nexus/content/repositories/nss-releases/com/ericsson/nss/EDE-Stats/EDE_Stats_CXP9034659/" + edeStats_rollout_version + "/EDE_Stats_CXP9034659-" + edeStats_rollout_version + ".tar\" -o EDE_Stats_CXP9034659.tar")
    run("curl -L \"" + edeStats_rollout_version + "\" -o EDE_Stats_CXP9034659.tar")
    run("mv EDE_Stats_CXP9034659.tar /EDE_Stats_CXP9034659.tar")
    run("cd /;chmod 777 EDE_Stats_CXP9034659.tar")
    run("tar -xf /EDE_Stats_CXP9034659.tar -C /")
    run("cd /EDE_Stats_CXP9034659")
    run("bash /EDE_Stats_CXP9034659/install.sh")

@task
def netsim_run(nssRelease,recording_file_version,edeStatsCheck='False',deplType="NSS",counterVolume="None",oss_enabled="False", oss_bulk_pm_enabled="False"):
    env.user = "netsim"
    env.password = "netsim"
    upload_rhosts()
    sim_data_list = get_sim_data(deplType,edeStatsCheck)
    upload_cfg(nssRelease, sim_data_list,edeStatsCheck,deplType,counterVolume,oss_enabled)
    if edeStatsCheck == "True":
        rollout_edeStats()
    #if get_hostname() != "netsim" and deplType == "NSS":
    #    remove_unstarted_node_tmpfs_dirs()
    download_record_file(recording_file_version)
    unzip_record_file()
    #* prevents list being converted to tuple by var args
    get_eutran_data(edeStatsCheck,deplType,*sim_data_list)
    generate_templates()
    rollout_genstats(oss_bulk_pm_enabled)


@task
def read_nrm_value():
    env.user = 'netsim'
    env.password = 'netsim'
    return_status, fetched_value = False, None
    if exists(NRM_DETAILS_FILE):
        nrm_details_object = StringIO()
        get(NRM_DETAILS_FILE, nrm_details_object)
        nrm_details_list = filter(None, (nrm_details_object.getvalue()).split('\n'))
        if nrm_details_list:
            ''' Provided value in file : NRM=NRM6 '''
            for line in nrm_details_list:
                if line.startswith('NRM='):
                    fetched_value = line.strip().replace(' ', '').split('=')[1]
                    if fetched_value:
                        if fetched_value == 'NRM1.3':
                            fetched_value = 'NRM5'
                        if fetched_value in SUPPORTED_AUTO_DETECT_DEPLOYMENTS:
                            return_status = True
                            print 'INFO : NETSIM_HOST : ' + str(env.host.split('.')[0]) + ' is configured for DEPLOYMENT_TYPE : ' + fetched_value
                        else:
                            print 'ERROR : NRM value ' + fetched_value + ' defined in ' + NRM_DETAILS_FILE + ' file is not supported by Genstats AUTO_DETECT_NRM feature for HOST : ' + str(env.host.split('.')[0]) + \
                            '. Terminating Genstats roll out for specific host as DYNAMIC NRM Roll out can not be performed.\n' + \
                            'Contact SIMNET/NETSIM Team for further assistance for resolving this issue.'
                            print 'INFO : Supported NRM by AUTO_DETECT_NRM feature is : ' + ', '.join(SUPPORTED_AUTO_DETECT_DEPLOYMENTS) + '.'
                    else:
                        print 'ERROR : NRM value not defined in ' + NRM_DETAILS_FILE + ' file for HOST : ' + str(env.host.split('.')[0]) + \
                        '. Terminating Genstats roll out for specific host as DYNAMIC NRM Roll out can not be performed.\n' + \
                        'Contact SIMNET/NETSIM Team for further assistance for resolving this issue.'
                    return return_status, fetched_value
            print 'ERROR : NRM value not defined in ' + NRM_DETAILS_FILE + ' file for HOST : ' + str(env.host.split('.')[0]) + \
            '. Terminating Genstats roll out for specific host as DYNAMIC NRM Roll out can not be performed.\n' + \
            'Contact SIMNET/NETSIM Team for further assistance for resolving this issue.'
        else:
            print 'ERROR : ' + NRM_DETAILS_FILE + ' file is empty for HOST : ' + str(env.host.split('.')[0]) + \
            '. Terminating Genstats roll out for specific host as DYNAMIC NRM Roll out can not be performed.\n' + \
            'Contact SIMNET/NETSIM Team for further assistance for resolving this issue.'
    else:
        print 'ERROR : ' + NRM_DETAILS_FILE + ' file does not exist for HOST : ' + str(env.host.split('.')[0]) + \
        '. Terminating Genstats roll out for specific host as DYNAMIC NRM Roll out can not be performed.\n' + \
        'Contact SIMNET/NETSIM Team for further assistance for resolving this issue.'
    return return_status, fetched_value


@parallel(pool_size=25)
@with_settings(warn_only=True)
@task
def auto_rollout(rpm_version="RELEASE", nssRelease="16.8", recording_file_version="RELEASE", deplType="NSS", edeStatsCheck="False", counterVolume="None", oss_enabled="False", oss_nodeMOMVer="18.01.2", oss_nwXMLpath="", oss_bulk_pm_enabled="False"):

    process_go_ahead = True
    if deplType.upper() == 'AUTO_DETECT_NRM':
        process_go_ahead, deplType = read_nrm_value()
    if process_go_ahead:
        disable_cron()
        disable_root_cron()
        disable_root_remount_cron()
        remove_old_recording_file()
        root_run(rpm_version)
        if oss_enabled == "True":
            install_netsim_stub_OSS(deplType, oss_nodeMOMVer, oss_nwXMLpath)
        if deplType != 'NSS' and deplType != 'NRM1.2':
            if exists(SGSN_REAL_DATA, use_sudo=False):
                set_permission_for_ebs_realdata()
        netsim_run(nssRelease, recording_file_version,edeStatsCheck,deplType,counterVolume,oss_enabled,oss_bulk_pm_enabled)


@parallel(pool_size=5)
@with_settings(warn_only=True)
@task
def health_check(edeStatsCheck="False"):
    env.user = "netsim"
    env.password = "netsim"
    run("bash /netsim_users/hc/bin/genstat_report.sh")
    if edeStatsCheck == "True":
        run("bash /EDE_Stats_CXP9034659/EDE_Stats_CXP9034659/bin/EdeStatsHealthCheck.sh")
    if exists(QA_LOG_FILE, use_sudo=False):
        fd = StringIO()
        get(QA_LOG_FILE, fd)
        QA_logs=fd.getvalue()
        QA_logs_list = filter(None, QA_logs.split('\n'))
        for line in QA_logs_list:
            if 'error' in line.lower():
                print "Log File " + QA_LOG_FILE + " have issues. Exiting Genstats's post health check"
                sys.exit(1)
    else:
        print "Log File " + QA_LOG_FILE + " does not exist"


@parallel(pool_size=5)
@with_settings(warn_only=True)
@task
def auto_nrm_health_check(auto_detect_nrm, edeStatsCheck="False"):
    process_go_ahead = True
    if auto_detect_nrm.upper() == 'YES':
        process_go_ahead, fetched_nrm_value = read_nrm_value()
    if process_go_ahead:
        env.user = "netsim"
        env.password = "netsim"
        run("bash /netsim_users/hc/bin/genstat_report.sh")
        if edeStatsCheck == "True":
            run("bash /EDE_Stats_CXP9034659/EDE_Stats_CXP9034659/bin/EdeStatsHealthCheck.sh")
        if exists(QA_LOG_FILE, use_sudo=False):
            fd = StringIO()
            get(QA_LOG_FILE, fd)
            QA_logs=fd.getvalue()
            QA_logs_list = filter(None, QA_logs.split('\n'))
            for line in QA_logs_list:
                if 'error' in line.lower():
                    print "Log File " + QA_LOG_FILE + " have issues. Exiting Genstats's post health check"
                    sys.exit(1)
        else:
            print "Log File " + QA_LOG_FILE + " does not exist"


@task
def generate_templates():
    env.user = "netsim"
    env.password = "netsim"
    run("python /netsim_users/auto_deploy/bin/TemplateGenerator.py")


@task
def bulk_pm_oss(start_time, end_time):
    env.user = "netsim"
    env.password = "netsim"
    run("python /netsim_users/pms/bin/bulkPMFilesGenerator.py --start_time \"" + start_time + "\" --end_time \"" + end_time + "\"")

@task
def getallnotstatednodes():
    env.user = "netsim"
    env.password = "netsim"
    result = []
    output = run("echo '.show allsimnes' | /netsim/inst/netsim_pipe \n")
    for line in output.splitlines():
        if "not started" in line:
            result.append(line.split()[0])
    return result

from fabric.contrib.files import exists

@task
def get_sim_data(deplType,edeStatsCheck="False"):
    env.user = "netsim"
    env.password = "netsim"
    run("python /netsim_users/auto_deploy/bin/getSimulationData.py --edeStatsCheck "+ edeStatsCheck + " -D " + deplType)
    if exists(SIM_DATA_FILE, use_sudo=False):
        sim_data_io = StringIO()
        get(SIM_DATA_FILE, sim_data_io)
        sim_data=sim_data_io.getvalue()
        sim_data_list = filter(None, sim_data.split('\n'))
    else:
        print "ERROR: " + SIM_DATA_FILE + " does not exists.Exiting genstats autorollout."
        logging.error("ERROR: " + SIM_DATA_FILE + " does not exists.Exiting genstats autorollout.")
        sys.exit(1)
    return sim_data_list


@task
def remove_unstarted_node_tmpfs_dirs():
    env.user = "netsim"
    env.password = "netsim"
    # 1.8K VFARMs to have only first five nodes in every sim
    # Node deletion after 5 nodes to be done for 1.8K VFARM and VAPP
    # A file with name Simnet_15K / Simnet_1.8K helps to identify if the VFARM is 15K or 1.8K
    type_list = []
    if exists(VFARM_TYPE_DIR, use_sudo=False):
        type_list = run("ls " + VFARM_TYPE_DIR + " | grep -i content | egrep -i 'Simnet_1.8K|Simnet_5K'").split()

    if type_list or get_hostname() == "netsim":
        mounted_sim_dir_list = run('ls ' + TMPFS_DIR + ' | xargs -n 1 basename | grep -v xml_step').split()
        for sim_dir in mounted_sim_dir_list:
            sim_path = TMPFS_DIR + sim_dir
            run('cd ' + sim_path + ' && ls |sort | perl -ne \'print if $.>5\' | xargs rm -rf; cd -')


@task
def disable_cron():
    env.user = "netsim"
    env.password = "netsim"
    #Backup and remove any current genstats scripts from crontab
    run("crontab -l > /tmp/_backup_cron")
    run("crontab -l | grep -v \"/netsim_users\" > /tmp/_removed_cron; crontab /tmp/_removed_cron")

@task
def disable_root_cron():
    env.user = "root"
    env.password = "shroot"
    #Backup and remove root cron entries for limitbw
    run("crontab -l > /tmp/_backup_root_cron")
    run("crontab -l | grep -v \"limitbw\" > /tmp/_removed_root_cron; crontab /tmp/_removed_root_cron")

@task
def download_record_file(recording_file_version):
    env.user = "netsim"
    env.password = "netsim"
    cmd = "curl -L \"" + recording_file_version + "\" -o recording_files.zip"
    run(cmd)

@task
def remove_old_recording_file():
    env.user="root"
    env.password="shroot"
    #Delete older recording files
    run("rm -f /netsim/recording_files.zip")   #Added handle permision change done for release older than 21.09
    run("rm -rf /netsim/genstats/*")

@task
def unzip_record_file():
    env.user = "netsim"
    env.password = "netsim"
    run("mkdir -p /netsim/genstats")
    run("rm -rf " + LOGS_DIR)
    run("mkdir -p " + LOGS_DIR + "rollout_console")
    run("unzip -o recording_files.zip -d /netsim/genstats > /dev/null 2>&1")

@task
def get_eutran_data(edeStatsCheck,deplType,*args):
    env.user = "netsim"
    env.password = "netsim"
    if not args:
        sim_data_list = get_sim_data(deplType,edeStatsCheck)
    else:
        sim_data_list = args
    isLTEpresent = False
    isEUtranDataPresent = False
    eutrancell_data = ""
    sims_without_eutran = []
    run("truncate -s 0 " + EUTRANCELL_DATA_FILE)
    for sim_info in sim_data_list:
         sim_data = sim_info.split()
         sim_name = sim_data[1]
         node_name = sim_data[3]
         if "LTE" in sim_name and 'ERBS' in node_name:
             isLTEpresent = True
             eutrancell_data = "/netsim/netsimdir/" + sim_name + "/SimNetRevision/EUtranCellData.txt"
             if exists(eutrancell_data, use_sudo=False):
                 run("cat " + eutrancell_data + " >> " + EUTRANCELL_DATA_FILE)
                 isEUtranDataPresent = True
             else:
                 sims_without_eutran.append(sim_name)
    incorrect_data = run("grep -E 'pERBS00.*\-1[3-9]' " + EUTRANCELL_DATA_FILE)
    incorrect_data_list = []
    incorrect_data_list = filter(None,incorrect_data.splitlines())
    for remove_data in incorrect_data_list:
         run("sed -i '/" + remove_data + "/d'  '" + EUTRANCELL_DATA_FILE + "' ")

    if sims_without_eutran:
        if deplType != 'NRM1.2':
            logging.error(" cannot find EUtranCellData.txt for " + ','.join(sims_without_eutran))
            print "ERROR: cannot find EUtranCellData.txt for " + ','.join(sims_without_eutran)
            sys.exit(1)
        else:
            logging.warning(" cannot find EUtranCellData.txt for " + ','.join(sims_without_eutran))
            print "WARNING: cannot find EUtranCellData.txt for " + ','.join(sims_without_eutran)
    elif not sims_without_eutran and isLTEpresent:
        if deplType == 'NRM1.2':
            netsim_file_name = get_hostname()
            run("echo '' >> /tmp/" + netsim_file_name)
            run("echo 'ERBS_CELLS_CONFIG_LIST=\"1 3 6 12\"' >> /tmp/" + netsim_file_name)

    if exists(EUTRANCELL_DATA_FILE, use_sudo=False):
        backup_eutran = EUTRANCELL_DATA_FILE + "_backup"
        run("cat " + EUTRANCELL_DATA_FILE + " | sort -u > " + backup_eutran)
        run("rm -f " + EUTRANCELL_DATA_FILE)
        run("mv " +  backup_eutran + " " + EUTRANCELL_DATA_FILE)

    if isLTEpresent:
        if deplType != 'NRM1.2':
            if not exists(EUTRANCELL_DATA_FILE, use_sudo=False) or not isEUtranDataPresent:
                print 'ERROR: Either ' + EUTRANCELL_DATA_FILE + ' file not present or ' + EUTRANCELL_DATA_FILE + ' file is empty.'
                logging.error("ERROR: Either ' + EUTRANCELL_DATA_FILE + ' file not present or ' + EUTRANCELL_DATA_FILE + ' file is empty.")
                print 'INFO: Exiting process.'
                sys.exit(1)


@task
def independent_sim_setup(sim_list=[], auto_detect=False, templates=False, cfgUpdate=False):
    env.user = "netsim"
    env.password = "netsim"

    if auto_detect:
        if templates:
            run("python /netsim_users/auto_deploy/bin/RolloutSims.py --auto_detect True --templates True")
        if cfgUpdate:
            run("python /netsim_users/auto_deploy/bin/RolloutSims.py --auto_detect True --cfgUpdate True")
    else:
        if templates:
            run("python /netsim_users/auto_deploy/bin/RolloutSims.py --sim " + "'" + sim_list + "'" + " --templates True")
        if cfgUpdate:
            run("python /netsim_users/auto_deploy/bin/RolloutSims.py --sim " + "'" + sim_list + "'" + " --cfgUpdate True")

def get_bsc_list():
    bsc_sim_list = []
    bsc_sim_list = run('ls ' + SIMULATION_DIR + ' | grep BSC').split("\n")
    if bsc_sim_list:
        return bsc_sim_list
    else:
        return None

def get_msc_list():
    msc_sim_list = []
    msc_sim_list = run('ls ' + SIMULATION_DIR + ' | grep MSC').split("\n")
    if msc_sim_list:
        return msc_sim_list
    else:
        return None

def get_hlr_list():
    hlr_sim_list = []
    hlr_sim_list = run('ls ' + SIMULATION_DIR + ' | grep -e "HLR-FE" -e "vHLR"').split("\n")
    if hlr_sim_list:
        return hlr_sim_list
    else:
        return None

def get_ecs_list():
    ecs_sim_list = []
    ecs_sim_list = run('ls ' + SIMULATION_DIR + ' | egrep "ERSN|ERS[-_]SN[-_]ESC|ERS[-_]SN[-_]SCU|SCU[-_]"').split("\n")
    if ecs_sim_list:
        return ecs_sim_list
    else:
        return None

@task
def end_to_end_sim_setup(sim_list=[], rpm_version="RELEASE", nssRelease="17.10", recording_file_version="RELEASE"):
    env.user = "netsim"
    env.password = "netsim"
    if sim_list:
        sim_list_move_command = ""
        sim_list = sim_list.split()
        for sim in sim_list:
            sim_list_move_command = sim_list_move_command + "|" + sim
        sim_list_move_command = sim_list_move_command.strip("|")
        sim_list_move_command = "for sim in `ls " + SIMULATION_DIR + " | egrep -v " + "'" + sim_list_move_command + "'" + "`;do mv " + SIMULATION_DIR + "$sim " + SIM_DIR + ";done"
        run(sim_list_move_command)
        auto_rollout(rpm_version, nssRelease, recording_file_version)
        sim_list_move_back_command = "for sim in `ls " + SIM_DIR + " | grep -v  netsimdir`;do mv " + SIM_DIR + "$sim " + SIMULATION_DIR + ";done"
        health_check()
        run(sim_list_move_back_command)
    else:
        print "WARN: Please mention required SIM(S) in SIMULATION_LIST_FOR_INDIVIDUAL_SETUP block for which Genstats Setup is required."

@task
def set_pmstmpfs():
    env.user = "root"
    env.password = "shroot"
    if not exists(TMPFS_DIR, use_sudo=False):
        run("mkdir "+ TMPFS_DIR)
    run("umount " + TMPFS_DIR)
    run("mount " + TMPFS_DIR)
    run("chmod 777 " + TMPFS_DIR)

def set_permission_for_ebs_realdata():
    env.user = "root"
    env.password = "shroot"
    run("chown -R netsim " + SGSN_REAL_DATA)
    run("chgrp -R netsim " + SGSN_REAL_DATA)
    run("chmod 777 -R " + SGSN_REAL_DATA)

def get_playback_list(edeStatsCheck):
    if exists(PLAYBACK_CFG, use_sudo=False):
       playback_content = run("grep NE_TYPE_LIST " + PLAYBACK_CFG).strip()
    else:
       logging.warning(" cannot find " + PLAYBACK_CFG)
       print "WARNING: cannot find " + PLAYBACK_CFG
       return None
    PLAYBACK_SIM_LIST = []
    PLAYBACK_SIM_LIST = playback_content.split("=")[-1].replace("\"", "").split()
    if edeStatsCheck == "True":
       PLAYBACK_SIM_LIST = [sim for sim in PLAYBACK_SIM_LIST if sim not in EDE_SUPPORTED_TRANSPORT_SIM_LIST]
    return PLAYBACK_SIM_LIST

@task
def set_VTF_FilePath():
    env.user = "netsim"
    env.password = "netsim"
    run("echo '' >> /netsim/netsim_cfg")
    run("echo 'VTFRADIONODE_PMEvent_FileLocation=\"/pm_data/\"' >> /netsim/netsim_cfg")

@task
def mount_VTF_FilePath():
    env.user = "root"
    env.password = "shroot"
    run("/netsim_users/pms/bin/createTempFsMountForNodes.sh")

@task
def deploy_cm_topology(pkg_version,bulk_cm_check,topology_check):
    env.user = "root"
    env.password = "shroot"
    run("curl  -L \"https://arm1s11-eiffel004.eiffel.gic.ericsson.se:8443/nexus/content/repositories/assure-releases/com/ericsson/eniq/netanserver/features/ERICCMTopology/" + pkg_version + "/ERICCMTopology-" + pkg_version + ".zip" + "\" -o /tmp/ERICCMTopology.zip")
    run("unzip /tmp/ERICCMTopology.zip -d /netsim/")
    run("chown -R netsim:netsim /netsim/ERICCMTopology")
    run("chmod -R 755 /netsim/ERICCMTopology")
    run("rm -rf /tmp/ERICCMTopology.zip")
    if bulk_cm_check.lower() == "true":
        generate_bulk_cm()

    if topology_check.lower() == "true":
        generate_topology_flag()
@task
def generate_bulk_cm():
    env.user = "netsim"
    env.password = "netsim"
    run("bash /netsim/ERICCMTopology/BULK_CM/bin/bulkcm.sh")

@task
def generate_topology_flag():
    env.user = "netsim"
    env.password = "netsim"
    run("touch /netsim/ERICCMTopology/.toplogyrolloutcheck")

@task
def perform_ecs_setup():
    env.user = "netsim"
    env.password = "netsim"
    run("rm -rf /netsim_users/pms/bcp_templates")
    run("cp -rf /netsim/genstats/bcp_templates /netsim_users/pms/")
    run("cd /netsim_users/pms/bcp_templates; wget https://arm901-eiffel004.athtem.eei.ericsson.se:8443/nexus/content/repositories/nss-releases/com/ericsson/nss/Genstats/genstats/1.0.2/genstats-1.0.2.zip; unzip genstats-1.0.2.zip;")

@task
def disable_root_remount_cron():
    env.user = "root"
    env.password = "shroot"
    #Backup and remove root cron entries for remounting
    if run("crontab -l | grep \"remounting.sh\""):
       run("crontab -l > /tmp/_backup_root_cron_1")
       run("crontab -l | grep -v \"remounting.sh\" > /tmp/_removed_root_remount_cron; crontab /tmp/_removed_root_remount_cron")

    #Backup and remove root cron entries for remounting
    elif run("crontab -l | grep \"NR_Remount\""):
       run("crontab -l > /tmp/_backup_root_cron_1")
       run("crontab -l | grep -v \"NR_Remount\" > /tmp/_removed_root_NRremount_cron; crontab /tmp/_removed_root_NRremount_cron")
    else:
       print "EDE & 5G tool is not present"
