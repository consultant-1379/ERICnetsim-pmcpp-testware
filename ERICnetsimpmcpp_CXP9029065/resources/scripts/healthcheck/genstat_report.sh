#!/bin/bash
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
# Version no    :  NSS 17.14
# Purpose       :  This script is responisible for initiating health check w.r.t stats and events workload.
# Jira No       :  NSS-14089
# Gerrit Link   :
# Description   :  Celltrace and Uetrace file generation for VTFRadioNode
# Date          :  17/08/2017
# Last Modified :  arwa.nawab@tcs.com
####################################################

BIN_DIR=`dirname $0`
BIN_DIR=`cd ${BIN_DIR} ; pwd`
. /netsim/netsim_cfg

QA_LOG_FILE="/netsim/genstats/logs/genstatsQA.log"

echo "INFO: Starting GenStats rollout verification "

# print installed genStats RPM version
RPM_VERSION=`rpm -q ERICnetsimpmcpp_CXP9029065`
echo "INFO: genStats RPM version: ${RPM_VERSION}"

if [ -f ${QA_LOG_FILE} ]; then
    rm -rf ${QA_LOG_FILE}
    echo "INFO: removed existing ${QA_LOG_FILE} "
fi

if [ ! -f /netsim/genstats/tmp/sim_data.txt ]; then
    echo "INFO: Generating /netsim/genstats/tmp/sim_data.txt file."
    /netsim_users/auto_deploy/bin/getSimulationData.py
    echo "INFO: /netsim/genstats/tmp/sim_data.txt file generated."
fi

START_TIMESTAMP=$(date "+%F %T %Z")
echo "INFO: GenStats QA logging started: ${START_TIMESTAMP}" >> ${QA_LOG_FILE}

# remove old log files
/netsim_users/pms/bin/removeLogFiles.py

# execute 15 min ROP
crontab -l | grep -i gpeh | sed 's/.* \* \//\//' | while read line
do
command=$(echo $line | sed 's/ >> .*//')
log_file=$(echo $line | rev | cut -d' ' -f2 | rev)
$command >> $log_file
done &
/netsim_users/pms/bin/genStats -r 15 >> /netsim_users/pms/logs/genStats_15min.log 2>&1 &
/netsim_users/pms/bin/lte_rec.sh -r 15 >> /netsim_users/pms/logs/lte_rec_15min.log 2>&1 &
/netsim_users/pms/bin/startPlaybacker.sh -r 15 >> /netsim_users/pms/logs/playbacker_15min.log 2>&1 &
/netsim_users/pms/bin/wran_rec.sh -l DEFAULT -r 15 >> /netsim_users/pms/logs/wran_rec.log 2>&1 &
wait

SIM_LIST=`eval echo '$'${HOSTNAME/-/_}_list`

MME_SIM_LIST=`eval echo '$'${HOSTNAME/-/_}_mme_list`

SIM_LIST="${SIM_LIST} ${MME_SIM_LIST} ${PLAYBACK_SIM_LIST}"

CONSOLIDATED_SIM_LIST=`echo ${SIM_LIST//[[:blank:]]/}`

if [[ ! -z ${CONSOLIDATED_SIM_LIST} ]]; then
    if [[ ! -z ${PLAYBACK_SIM_LIST} ]];then
        python ${BIN_DIR}/genstats_checking.py -l ${SIM_LIST} -ul ${LTE_UETRACE_LIST} ${MSRBS_V1_LTE_UETRACE_LIST} ${MSRBS_V2_LTE_UETRACE_LIST} ${VTF_UETRACE_LIST} -b ${SET_BANDWIDTH_LIMITING} -recwl ${RECORDING_WORKLOAD_LIST} -statswl ${STATS_WORKLOAD_LIST} -gpehwl ${GPEH_WORKLOAD_LIST} -rbsgpehwl ${GPEH_RBS_WORKLOAD} -gpehmpcells ${GPEH_MP_CONFIG_LIST} -playbacksimlist ${PLAYBACK_SIM_LIST} -deployment ${TYPE}
    else
        python ${BIN_DIR}/genstats_checking.py -l ${SIM_LIST} -ul ${LTE_UETRACE_LIST} ${MSRBS_V1_LTE_UETRACE_LIST} ${MSRBS_V2_LTE_UETRACE_LIST} ${VTF_UETRACE_LIST} -b ${SET_BANDWIDTH_LIMITING} -recwl ${RECORDING_WORKLOAD_LIST} -statswl ${STATS_WORKLOAD_LIST} -gpehwl ${GPEH_WORKLOAD_LIST} -rbsgpehwl ${GPEH_RBS_WORKLOAD} -gpehmpcells ${GPEH_MP_CONFIG_LIST} -deployment ${TYPE}
    fi
fi

END_TIMESTAMP=$(date "+%F %T %Z")
echo "INFO: GenStats QA logging ended: ${END_TIMESTAMP}" >> ${QA_LOG_FILE}
echo "INFO: GenStats rollout verification complete"
