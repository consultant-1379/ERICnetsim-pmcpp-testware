#!/bin/bash

################################################################################
# COPYRIGHT Ericsson 2023
#
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
################################################################################

###################################################
# Version no    :  NSS 23.12
# Purpose       :  Script creates and mounts real node file path if configured for any node type.
# Jira No       :  NSS-43613
# Gerrit Link   :  https://gerrit.ericsson.se/#/c/15097687/
# Description   :  Adding support for new extra product data file type
# Date          :  29/04/2023
# Last Modified :  vadim.malakhovski.ext@ericsson.com
####################################################

# XSURJAJ
#
# This script is responsible to create PM and PMEVENT file location directories
# under Node file system and temp file system including mount binding between them
#
#

. /netsim/netsim_cfg > /dev/null 2>&1

BIN_DIR=`dirname $0`
BIN_DIR=`cd ${BIN_DIR} ; pwd`

. ${BIN_DIR}/functions

SIM_DIR="/netsim/netsim_dbdir/simdir/netsim/netsimdir"
OUT_ROOT="/pms_tmpfs"

if [ -z "${EPG_PM_FileLocation}" ] ; then
     EPG_PM_FileLocation="/var/log/services/epg/pm/"
fi

# Create mount binding between node file system
# temp file system
createMount() {

    SIM=$1
    FILE_PATH=$2
    SIM_TYPE=$3
    SIM_NAME=''

    if [[ ${SIM_TYPE} == LTE ]];then
        SIM_NAME=`ls ${SIM_DIR} | grep -i "\-${SIM}" `
    elif [[ ${SIM_TYPE} == WRAN ]];then
        SIM_NAME=`ls ${SIM_DIR} | grep -w  "${SIM}" `
    else
        SIM_NAME=`ls ${SIM_DIR} | grep -w ${SIM} `
    fi

    if [ $? -eq 0 ] ; then

        NODE_LIST=`ls ${SIM_DIR}/${SIM_NAME}`
        
        for NODE in ${NODE_LIST} ; do

            if ! grep -q ${NODE} "/tmp/showstartednodes.txt"; then
                continue
            fi

            NODE_PATH="${SIM_DIR}/${SIM_NAME}/${NODE}/fs/${FILE_PATH}/"
            NODE_TEMP_PATH="${OUT_ROOT}/${SIM}/${NODE}/${FILE_PATH}/"
            
            if [[ ! -d "${NODE_PATH}" ]] ; then 
                mkdir -p "${NODE_PATH}"
            fi
            chown -R netsim:netsim "${SIM_DIR}/${SIM_NAME}/${NODE}/fs"

            if [[ ! -d "${NODE_TEMP_PATH}" ]] ; then 
                mkdir -p "${NODE_TEMP_PATH}" 
            fi
            chown -R netsim:netsim "${OUT_ROOT}/${SIM}/${NODE}"
            
            # if not already mounted then mount
            if [[ ! $(findmnt "${NODE_PATH}") ]] ; then             
                mount -B ${NODE_TEMP_PATH} ${NODE_PATH}
                mount -a                                 
            fi
        done
    else
        log " $SIM not found"
    fi
}


createCustomizedMountingPoint(){
    if [[ ! -d "${dest_path}" ]] ; then 
        mkdir -p "${dest_path}"      
    fi   
    chown -R netsim:netsim "${dest_path}"
    
    if [[ ! -d "${src_path}" ]] ; then 
        mkdir -p "${src_path}"
    fi
    chown -R netsim:netsim "${src_path}" 
    
    # if not already mounted then mount
    if [[ ! $(findmnt "${dest_path}") ]] ; then   
        mount -B ${src_path} ${dest_path}
        mount -a
    fi
    
}


createTempFsMounting() {

   log "createTempFsMountForNodes start"

   if [[ ! -z ${src_path} ]] && [[ ! -z ${dest_path} ]]; then
       createCustomizedMountingPoint
       exit 0
   fi

   for SIM in $LIST ; do
        if grep -q $SIM "/tmp/showstartednodes.txt"; then

            NODE_TYPE=""

            SIM_TYPE=`getSimType ${SIM}`

            if [ "${SIM_TYPE}" = "WRAN" ] || [ "${SIM_TYPE}" = "RBS" ]; then               
                
                #Check for DG2 nodes
                MSRBS_V2_LIST=`ls ${OUT_ROOT}/${SIM} | grep MSRBS-V2`
                #Check for PRBS nodes
                PRBS_LIST=`ls ${OUT_ROOT}/${SIM} | grep PRBS`
                #Check for RBS nodes
                RBS_LIST=`ls ${OUT_ROOT}/${SIM} | grep RBS`
                if [ ! -z "${MSRBS_V2_LIST}" ] ; then
                    NODE_TYPE="MSRBS_V2"
                elif [ ! -z "${PRBS_LIST}" ] ; then
                    NODE_TYPE="PRBS"
                elif [ ! -z "${RBS_LIST}" ] ; then
                    NODE_TYPE="RBS"
                else
                    NODE_TYPE="RNC"
                fi

            elif [ "${SIM_TYPE}" = "LTE" ] ; then
                MSRBS_V1_LIST=`ls ${OUT_ROOT}/${SIM} | grep pERBS`
                MSRBS_V2_LIST=`ls ${OUT_ROOT}/${SIM} | grep dg2ERBS`
                if [ ! -z "${MSRBS_V1_LIST}" ] ; then
                    NODE_TYPE="MSRBS_V1"
                elif [ ! -z "${MSRBS_V2_LIST}" ] ; then
                    NODE_TYPE="MSRBS_V2"
                fi
            elif  [ "${SIM_TYPE}" = "GNODEBRADIO" ] ; then
                NODE_TYPE="GNODEBRADIO"
            elif [ "${SIM_TYPE}" = "TCU04" ] || [ "${SIM_TYPE}" = "C608" ] ; then
                NODE_TYPE="TCU04"
            elif [ "${SIM_TYPE}" = "TCU03" ] ; then
                NODE_TYPE="TCU"
            elif [ "${SIM_TYPE}" = "GSM_DG2" ] ; then
                NODE_TYPE="MSRBS_V2"
            elif [ "${SIM_TYPE}" = "HSS" ] ; then
                NODE_TYPE="HSS_FE"
            elif [ "${SIM_TYPE}" = "EPG-SSR" ] || [ "${SIM_TYPE}" = "EPG-EVR" ]; then
                NODE_TYPE="EPG"
            elif [ "${SIM_TYPE}" = "VBGF" ] ; then
                NODE_TYPE="MRSV"
            elif [ "${SIM_TYPE}" = "MRF" ] ; then
                NODE_TYPE="MRFV"
            elif [ "${SIM_TYPE}" = "5GRADIONODE" ] ; then
                NODE_TYPE="FIVEGRADIONODE"
            elif [ "${SIM_TYPE}" = "SHARED-CNF" ] ; then
                NODE_TYPE="SHARED_CNF"
            else
                NODE_TYPE="${SIM_TYPE}"
            fi

            # For STATS
            ne_file_location="${NODE_TYPE}"_PM_FileLocation
            PMDIR=${!ne_file_location}

            if [ ! -z "${PMDIR}" ] ; then
                createMount "${SIM}" "${PMDIR}" "${SIM_TYPE}"
            fi

            # For EVENTS
            ne_file_location="${NODE_TYPE}"_PMEvent_FileLocation
            PMDIR=${!ne_file_location}

            if [ ! -z "${PMDIR}" ] ; then
                createMount "${SIM}" "${PMDIR}" "${SIM_TYPE}"
            fi
            
            #For Product Data
            ne_file_location="${NODE_TYPE}"_PMPD_FileLocation
            PMDIR=${!ne_file_location}
            if [ ! -z "${PMDIR}" ] ; then
                createMount "${SIM}" "${PMDIR}" "${SIM_TYPE}"
            fi
        fi
    done
    log "createTempFsMountForNodes end"
}

src_path=$1
dest_path=$2

createTempFsMounting
