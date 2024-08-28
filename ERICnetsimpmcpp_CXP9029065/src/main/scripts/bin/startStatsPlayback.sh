#!/bin/bash

################################################################################
# COPYRIGHT Ericsson 2022
#
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
################################################################################

###################################################
# Version no    :  NSS 23.17
# Purpose       :  The purpose of this script to call playbackGenerator framework to generate STATS PM files.
# Jira No       :  NSS-45946
# Gerrit Link   :  https://gerrit.ericsson.se/#/c/16375691/
# Description   :  Did code changes to alow the mounting script in RV
# Date          :  17/10/2023
# Last Modified :  surendra.mattaparthi@tcs.com
####################################################

#Fetching input arguments
PM_DIR=${1}
APPEND_PATH=${2}
NE_TYPE=${3}
FILE_FORMAT=${4}
OUTPUT_TYPE=${5}
INPUT_LOCATION=${6}
DATE=${7}
ROP_START_TIME=${8}
ROP_END_TIME=${9}
INSTALL_DIR=${10}
LOG=${11}
FINAL_MAPPED_FILE=${12}
PROCESS_TYPE=${13}
ROP_PERIOD=${14}
ROP_END_DATE=${15}
EXEC_FROM_HC=${16}
dur=${19}
UNIQUE_ID="99999"
CREATE_MOUNT_SCRIPT="/netsim_users/pms/bin/createTempFsMountForNodes.sh"
first_run=0

if [[ $NE_TYPE == *"SBG-IS"* ]]; then
    UNIQUE_ID=${17}
elif [[ $NE_TYPE == *"HSS-FE-TSP"* ]] || [[ $NE_TYPE == *"MTAS-TSP"* ]] || [[ $NE_TYPE == *"CSCF-TSP"* ]] || [[ $NE_TYPE == *"SAPC-TSP"* ]] || [[ $NE_TYPE == *"vEIR-FE"* ]] || [[ $NE_TYPE == *"EIR-FE"* ]]  || [[ $NE_TYPE == *"VCUDB"* ]]; then
    MEASUREMENT_JOB_ID_MPID=${17}
    MEASUREMENT_JOB_ID=`echo $MEASUREMENT_JOB_ID_MPID | cut -d":" -f1`
    MP_COUNT=`echo $MEASUREMENT_JOB_ID_MPID | cut -d":" -f2`
    if [[ ! $NE_TYPE == *"EIR-FE"* ]]; then
       MP_START=`echo $MEASUREMENT_JOB_ID_MPID | cut -d":" -f3`
       TSP_MPID_TIME_START_DATETIME=${18}
    fi
elif [[ $NE_TYPE == *"FrontHaul"* ]] && [[ $dur == "900" ]] || [[ $dur == "60" ]] || [[ $dur == "86400" ]]; then
    FILE_beginTime=${17}
    FILE_endTime=${18}
    dur=${19}
elif [[ $NE_TYPE == *"SCEF"* ]]; then
    FILE_TYPE=${17}
elif [[ $NE_TYPE == *"gNodeBRadio"* ]]; then
    HARDWARE_NAME=${17}
fi

NRM_CHECK=1
MD_1_CHECK=1

DEPL_TYPE=$(cat /netsim/netsim_cfg | grep -v '#' | grep 'TYPE=' | awk -F'"' '{print $2}')

if [[ ${DEPL_TYPE} == *"NRM"* ]] ; then
    NRM_CHECK=0
elif [[ ${DEPL_TYPE} == "MD_1" ]] ; then
    MD_1_CHECK=0
fi

LOOP_INSTANCE=1

#logging
log() {

    MSG=$1

    TS=`date +"%Y-%m-%d %H:%M:%S"`
    echo "${TS} ${MSG}"
}

#Create mounting for node path in pms_tmpfs and netsim_dbdir 
mountOutputDir() {

    OUTDIR=$1
    NODEDIR=$2

    mkdir -p ${OUTDIR}
    if [[ -d ${OUTDIR} ]];then
        echo "INFO: createTempFsMountForNodes.sh"
        echo shroot | su root -c "${CREATE_MOUNT_SCRIPT} ${OUTDIR} ${NODEDIR}"
        if [ $? -ne 0 ] ; then
            echo "ERROR: createTempFsMountForNodes.sh failed"
            exit 1
        fi
    fi
}

generatePmFile(){

    NEW_FILE_NAME=$(echo ${FILE_FORMAT} | sed "s/<DATE>/${DATE}/; s/<ROP_START_TIME>/${ROP_START_TIME}/; s/<ROP_END_TIME>/$ROP_END_TIME/; s/<ROP_END_DATE>/${ROP_END_DATE}/; s/<MEASUREMENT_JOB_NAME>/${MEASUREMENT_JOB_ID}/; s/<MANAGED_ELEMENT_ID>/${targetDir}/; s/<DOMAIN>/${sourceFileName}/; s/<HARDWARE_NAME>/${HARDWARE_NAME}/")

    for(( inst=1; inst <= ${LOOP_INSTANCE}; inst++ )); do
        FILE_NAME=$(echo ${NEW_FILE_NAME} | sed "s/UNIQUE_ID/$UNIQUE_ID/")
        outputFile=${OUTPUT_PATH}/${FILE_NAME}

        if [[ $NE_TYPE == *"SCEF"* ]] || [[ $NE_TYPE == *"vCU-UP"* ]] || [[ $NE_TYPE == *"vCU-CP"* ]];then
            outputSymlink=${SYMLINK_PATH}/${FILE_NAME}
        fi

        if [ $OUTPUT_TYPE == "COPY" ]; then
            if [[ $NE_TYPE == *"SBG-IS"* ]] && [[ ${MD_1_CHECK} -eq 0 ]] ; then
                if [[ ${first_run} -eq 0 ]]  ; then
                    first_run=1                   
                    # updating source template once per rop so that all other 300 files can be hardlinked to it
                    /${INSTALL_DIR}/playbackGenerator.sh $sourceFile $sourceFile -c $NE_TYPE $ROP_PERIOD $targetDir
                fi
                /${INSTALL_DIR}/playbackGenerator.sh $sourceFile  $outputFile -hl $NE_TYPE $ROP_PERIOD $targetDir
            else
                /${INSTALL_DIR}/playbackGenerator.sh $sourceFile $outputFile -c $NE_TYPE $ROP_PERIOD $targetDir
                if [[ $NE_TYPE == *"SCEF"* ]] && [[ $FILE_TYPE == B ]];then 
                     # create sym-links of file created in pms_tmpfs to netsim_dbdir
                    /${INSTALL_DIR}/playbackGenerator.sh $outputFile $outputSymlink -l $NE_TYPE $ROP_PERIOD $targetDir
                elif [[ $NE_TYPE == *"vCU-UP"* || $NE_TYPE == *"vCU-CP"* ]] && [[ ${MD_1_CHECK} -eq 0 ]] ;then 
                     # symlinking source to /pms_tmpfs because /pms_tmpfs and netsimdbir are mounted
                    /${INSTALL_DIR}/playbackGenerator.sh $sourceFile $outputFile -l $NE_TYPE $ROP_PERIOD $targetDir
                fi
            fi
        elif [ $OUTPUT_TYPE == "GZIP" ]; then
            /${INSTALL_DIR}/playbackGenerator.sh $sourceFile $outputFile -g $NE_TYPE $ROP_PERIOD $targetDir
        elif [ $OUTPUT_TYPE == "STAMPED" ]; then
            if [[ $NE_TYPE == *"FrontHaul-6080"* ]]; then
                /${INSTALL_DIR}/playbackGenerator.sh $sourceFile $outputFile -s $NE_TYPE $ROP_PERIOD $targetDir $FILE_beginTime $FILE_endTime $dur
            fi
        elif [ $OUTPUT_TYPE == "STAMPED_GZIP" ]; then
            if [[ $NE_TYPE == *"FrontHaul-6020"* ]] || [[ $NE_TYPE == *"FrontHaul-6000"* ]] || [[ $NE_TYPE == *"BSP"*  ]]; then
                /${INSTALL_DIR}/playbackGenerator.sh $sourceFile $outputFile -sg $NE_TYPE $ROP_PERIOD $targetDir $FILE_beginTime $FILE_endTime $dur
            fi
        elif [ $OUTPUT_TYPE == "ZIP" ]; then
             if [[ $NE_TYPE == *"SCEF"* ]] && [[ $FILE_TYPE == A ]] && ! [[ -z ${scef_a_type_identifier} ]]; then
                # A type zips creation in pms_tmpfs
                if [[ ${MD_1_CHECK} -eq 0 ]] ; then
                    /${INSTALL_DIR}/playbackGenerator.sh ${sourceFile} ${outputSymlink}.zip -l ${NE_TYPE} ${ROP_PERIOD} ${targetDir}
                else
                    /${INSTALL_DIR}/playbackGenerator.sh ${sourceFile} ${outputFile}.zip -c ${NE_TYPE} ${ROP_PERIOD} ${targetDir} ${DATE} ${ROP_START_TIME} ${ROP_END_TIME}
                    #create sym-links of file created in pms_tmpfs to netsim_dbdir
                    /${INSTALL_DIR}/playbackGenerator.sh ${outputFile}.zip ${outputSymlink}.zip -l ${NE_TYPE} ${ROP_PERIOD} ${targetDir}
                fi      
             fi
        elif [ $OUTPUT_TYPE == "TAR" ]; then 
            allSourceFilesString=`ls ${INPUT_LOCATION}/*`
            /${INSTALL_DIR}/playbackGenerator.sh "${allSourceFilesString}" "${outputFile}" -t "${NE_TYPE}" "${ROP_PERIOD}" "${targetDir}" "${DATE}" "${ROP_START_TIME}" "${ROP_END_TIME}"
        else
            /${INSTALL_DIR}/playbackGenerator.sh $sourceFile $outputFile -l $NE_TYPE $ROP_PERIOD $targetDir
        fi
        if [[ $NE_TYPE == *"SBG-IS"* ]]; then
           if [[ ${inst} -eq ${LOOP_INSTANCE} ]]; then
               UNIQUE_ID=1001
           else
               UNIQUE_ID=$((UNIQUE_ID+1))
           fi
        else
            UNIQUE_ID=$((UNIQUE_ID+1))
        fi
    done
}

for fname in `cat ${FINAL_MAPPED_FILE}`; do
    if [[ $NE_TYPE == *"SCEF"* ]];then
        sourceFileName=$(echo $fname | cut -d";" -f1 | sed 's/.zip//g' )
    fi													
    sourceFile=${INPUT_LOCATION}/$(echo $fname | cut -d";" -f1)
    targetDir=`echo $fname | cut -d";" -f2`
    scef_a_type_identifier=`echo $fname | cut -d";" -f3`

    if ! grep -q ${targetDir} "/tmp/showstartednodes.txt"; then
        continue
    fi

    if [[ $NE_TYPE == *"HSS-FE-TSP"* ]] || [[ $NE_TYPE == *"MTAS-TSP"* ]] || [[ $NE_TYPE == *"CSCF-TSP"* ]] || [[ $NE_TYPE == *"SAPC-TSP"* ]] ; then
        MP_END=`expr $MP_COUNT + $MP_START - 1`
        for MP in `seq $MP_START $MP_END`; do
           OUTPUT_PATH=$PM_DIR/$NE_TYPE/$targetDir/fs/$APPEND_PATH/MP${MP}_${TSP_MPID_TIME_START_DATETIME}
           if [ ! -d ${OUTPUT_PATH} ];then
               mkdir -p ${OUTPUT_PATH}
           fi
               generatePmFile
        done
    elif [[ $NE_TYPE == *SCEF* ]] || [[ $NE_TYPE == *"vCU-UP"* ]] || [[ $NE_TYPE == *"vCU-CP"* ]] || [[ $NE_TYPE == *SBG-IS* ]]; then
        OUTPUT_PATH=/pms_tmpfs/$NE_TYPE/$targetDir/$APPEND_PATH
        SYMLINK_PATH=$PM_DIR/$NE_TYPE/$targetDir/fs/$APPEND_PATH
        NODE_PATH=${PM_DIR}/${NE_TYPE}/${targetDir}/fs/${APPEND_PATH}/
    elif [[ $NE_TYPE == *"gNodeBRadio"* ]];then
        ORU_NUM=$(basename ${APPEND_PATH})
        STATUS_FILE=${PM_DIR}/${NE_TYPE}/${targetDir}/fs/${targetDir}_${ORU_NUM}_PM_STATUS.txt
        if [[ ! -f ${STATUS_FILE} ]];then
            continue
        else
            OUTPUT_PATH=/pms_tmpfs/${NE_TYPE}/${targetDir}/${APPEND_PATH}
            NODE_PATH=${PM_DIR}/${NE_TYPE}/${targetDir}/fs/${APPEND_PATH}
        fi
    elif [[ $NE_TYPE == *"WMG-OI"* ]] || [[ ${NE_TYPE} == *ECEE* ]] || [[ $NE_TYPE == *"vWMG-OI"* ]] || [[ $NE_TYPE == *"EPG-OI"* ]] || [[ $NE_TYPE == *"SBG-IS"* ]] || [[ $NE_TYPE == *"FrontHaul"* ]] || [[ $NE_TYPE == *"vAFG"* ]] || [[ $NE_TYPE == *"ADP"* ]];then
        OUTPUT_PATH=/pms_tmpfs/${NE_TYPE}/${targetDir}/${APPEND_PATH}/
        NODE_PATH=${PM_DIR}/${NE_TYPE}/${targetDir}/fs/${APPEND_PATH}/
    else
        OUTPUT_PATH=${PM_DIR}/${NE_TYPE}/${targetDir}/fs/${APPEND_PATH}/
    fi

    if [[ $NE_TYPE == *"gNodeBRadio"* ]] || [[ $NE_TYPE == *ECEE* ]] || [[ $NE_TYPE == *"WMG-OI"* ]] || [[ $NE_TYPE == *"vWMG-OI"* ]] || [[ $NE_TYPE == *"EPG-OI"* ]] || [[ $NE_TYPE == *"SBG-IS"* ]] || [[ $NE_TYPE == *"FrontHaul"* ]] || [[ $NE_TYPE == *"vCU-UP"* ]] || [[ $NE_TYPE == *"vCU-CP"* ]] || [[ $NE_TYPE == *"vAFG"* ]] || [[ $NE_TYPE == *"ADP"* ]];then
        if [[ ! -d ${OUTPUT_PATH} ]] && [[ ${OUTPUT_PATH} != *"/c/pm_data/"* ]];then
            # Execute mounting from HC as it will avoid parallel execution with crontab for all NRM deployments and NSS where nodes are started before rollout. HC is executed 1 time only during the rollout unlike the genstats scripts from crontab
            # OR If NSS deploymennt and nodes are started after the rollout hence HC was not executed. Only 15 min pass so that it does not clash with 1 mins crons.
            if [[ ${EXEC_FROM_HC} == "YES" ]] || [[ "${ROP_PERIOD}" = "15" ]] ;then
                   mountOutputDir ${OUTPUT_PATH} ${NODE_PATH}
            fi
        fi
    elif [[ ! -d ${OUTPUT_PATH} ]] && [[ $NE_TYPE != *SCEF* ]];then
       mkdir -p ${OUTPUT_PATH}
    elif [[ ! -d ${OUTPUT_PATH} ]] && [[ $NE_TYPE == *SCEF* ]];then
       mkdir -p ${OUTPUT_PATH} ${SYMLINK_PATH}
    fi

    if [[ $NE_TYPE == *"SBG-IS"* ]]; then
        if [[ ${NRM_CHECK} -eq 0 ]] || [[ ${MD_1_CHECK} -eq 0 ]] ; then
           LOOP_INSTANCE=300
        fi
    fi
    generatePmFile
done
