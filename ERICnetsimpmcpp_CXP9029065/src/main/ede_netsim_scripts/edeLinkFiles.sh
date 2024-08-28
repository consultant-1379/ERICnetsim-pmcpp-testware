#!/bin/bash
###############################################################################
###############################################################################
# COPYRIGHT Ericsson 2016
#
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
###############################################################################
###############################################################################
sourceDir=$1"/temp"
dataSource=`echo $2 | tr '[:lower:]' '[:upper:]'`

#Handling for logs in case of multiple data sources on multiple netsim boxes.
DATE=`date "+%Y_%m_%d_%H:%M:%S"`
INSTALL_DIR="$(cd $(dirname "$0") && pwd)"
if [ ! -d ${INSTALL_DIR}/logs/scripts_log_$dataSource ] ; then
        mkdir -p ${INSTALL_DIR}/logs/scripts_log_$dataSource
fi

LOG="${INSTALL_DIR}/logs/scripts_log_$dataSource/edeLinkProcess_${DATE}.$$.log"


###############################################
# Function: log_it
# Description: Logs the messages to the log file
# Arguments: One. The String to be logged
###############################################
log_it(){
  echo `date "+%Y_%m_%d_%H:%M:%S"` $1 >> $LOG
}

##########################################################################################################
# Function: Usage
# Description: This function display this tool usage information.
##########################################################################################################
Usage(){
        echo "Usage: ${INSTALL_DIR}/edeLinkFiles.sh  <EDE Intermediate location> <Data Source> <Netsim Output file location (optional> <Number of scripts (optional)> "
}


###################################################################################
# Function: ValidateArguments
# Description: This function validates and parses the command line.
# Returns:      0       Success
#               1       Error
#####################################################################################
ValidateArguments(){
   num_args=$1
   log_it "INFO:Parse Command Line..."
   if [ $num_args -lt 2 ] ; then
     log_it "ERROR: Insufficient argument passed."
     return 1
   fi
   return 0
}


###################################################################################
# Function: linkFiles
# Description: This function link all the files of input directory to output directory.
# Returns:      0       Success
#               1       Error
#####################################################################################
linkFiles(){

        targetDir="${INSTALL_DIR}/logs/batch_logs_$dataSource/batchfiles"$$
        rm -rf $targetDir
        mkdir -p $targetDir

        processed_rop_folder_list="$targetDir/processedRopFolderList"
        ls $sourceDir | grep "_processed" | grep -v "_linked"| sort > $processed_rop_folder_list
        processed_rop_folder_list_size=`cat $processed_rop_folder_list | wc -l | tr -d ' '`

        if [ $processed_rop_folder_list_size -eq 0 ] ; then
                log_it "Waiting for files to be processed. Please wait for next cycle to run"
                rm -rf $targetDir
                return 2
        else
                ropFolder=`cat $processed_rop_folder_list | tail -1 | tr -d ' '`
                ropFolderName=`echo $ropFolder | cut -d "_" -f1`
                sourceDir=$sourceDir"/"$ropFolder

                log_it "INFO: Distributing files among netsim output directory"
                completeFileList="$targetDir/allfilelist"

                if [ $dataSource == "CTUM" -o $dataSource == "LTEUETR" ]; then
                        ls -a1 $sourceDir/*/* | sort > $completeFileList
                else
                        ls $sourceDir | sort > $completeFileList
                fi
                log_it "Rop folder to be linked : ${ropFolder}"
                log_it "Temporary batch files directory is: $targetDir"
                log_it "Complete file list is $completeFileList"

                totalFileCountInROP=`cat $completeFileList | wc -l | tr -d ' '`
                log_it "Total file count: $totalFileCountInROP"

                if [ $dataSource == "CTUM" -o $dataSource == "EBM" -o $dataSource == "SGSN" -o $dataSource == "MME" -o $dataSource == "LTEUETR" ]; then
                        infoDir="${INSTALL_DIR}/logs/batch_logs_$dataSource/SimToNodeInfo"$$
                        rm -rf $infoDir
                        mkdir -p $infoDir

                        simToNodeInfoFileName=$infoDir/SimToNodeInfo_$$.txt
                    if [ ! -f "$simToNodeInfoFileName" ]; then
                                if [ $dataSource == "LTEUETR" ]; then
                                        echo ".show started" | /netsim/inst/netsim_shell | grep "LTE" >> $simToNodeInfoFileName
                                else
                                        echo ".show started" | /netsim/inst/netsim_shell | grep "SGSN" >> $simToNodeInfoFileName
                                fi
                    fi
                        simToNodeFileName=$infoDir/SimToNode_$$.txt
                        if [ ! -f "$simToNodeFileName" ]; then
                                #This code snippet is used to write by fetching SIMULATOR_NODE Mapping into file
                                while read line ; do arr=($line);if ! [ -z "${arr[6]// }" ]; then echo ${arr[6]};fi;done < $simToNodeInfoFileName >> $simToNodeFileName
                    fi
                fi

                #the part which distributes the files among child scripts
                factor=1
                mod=0
                start_index=1
                end_index=0

                if [ $number_of_scripts -gt $totalFileCountInROP ] ; then
                        number_of_scripts=$totalFileCountInROP
                        mod=-1
                else
                        factor=$((totalFileCountInROP / $number_of_scripts))
                        mod=$((totalFileCountInROP % $number_of_scripts))
                fi

                for(( c=0; c<$number_of_scripts; c++ ))
        do
            start_index=$((end_index+1))
            if [ $c -eq $((number_of_scripts-1)) ]; then
                end_index=$totalFileCountInROP
            else
                if [ $mod -gt 0 ] ; then
                    temp_add=1
                else
                    temp_add=0
                fi
                end_index=$(($end_index+$factor+$temp_add))
                mod=$((mod-1))
            fi

                if [ $dataSource == "EBM" -o $dataSource == "SGSN" -o $dataSource == "MME" ]; then
                /${INSTALL_DIR}"/"linkToNetsimChildForEBM.sh $sourceDir $baseOututDir $targetDir $LOG $c $start_index $end_index $simToNodeFileName &
                        elif [ $dataSource == "CTUM" ]; then
                                /${INSTALL_DIR}"/"linkToNetsimChildForCTUM.sh $sourceDir $baseOututDir $targetDir $LOG $c $start_index $end_index $simToNodeFileName &
            elif [ $dataSource == "LTEUETR" ]; then
                                /${INSTALL_DIR}"/"linkToNetsimChildForLUETR.sh $sourceDir $baseOututDir $targetDir $LOG $c $start_index $end_index $simToNodeFileName &
                        fi
        done
        fi
}

###################################################################################
# Function: linkFilesforCTR
# Description: This function link all the files of input directory to output directory for CTR datasource.
#####################################################################################
linkFilesForCTR(){
        ## This command ("${!1}") helps to get a value of an array passed as an argument to the method ##
    list_of_sim=("${!1}")

        ## Get only those sims whose files are present ##
        for sim_name in ${list_of_sim[@]}
        do
                sourceBatchFileName="${targetDir}/sourceBatchFile_${sim_name}"
                ls $sourceDir | grep ${sim_name}[A-Za-z] > $sourceBatchFileName
                totalFileCountInSim=`cat $sourceBatchFileName | tr -d ' ' | wc -l`
                if [[ ${totalFileCountInSim} -ne 0 ]]; then
                        log_it "Started script for  ${sim_name} with total file count :: $totalFileCountInSim"
                        /${INSTALL_DIR}"/"linkToNetsimChild.sh $sourceDir $baseOututDir $targetDir $LOG ${sim_name} $sourceBatchFileName &
                else
                        log_it "Ignoring ${sim_name} as files are not present"
                fi
        done
}

###################################################################################
# Function: setUpCTRFiles
# Description: This function groups the CTR files.
# Returns:      0       Success
#               1       Error
#####################################################################################
setUpCTRFiles(){

    sim_list_array=($(ls /pms_tmpfs/ | grep LTE))
    sim_count=${#sim_list_array[@]}
    if [ ${sim_count} -eq 0 ] ; then
        log_it "LTE simulations are not present on the server"
        exit -1
    fi

    targetDir="${INSTALL_DIR}/logs/batch_logs_$dataSource/batchfiles"$$
    rm -rf ${targetDir}
    mkdir -p ${targetDir}

    processed_rop_folder_list="$targetDir/processedRopFolderList"
    ls ${sourceDir} | grep "_processed" | grep -v "_linked" | sort > ${processed_rop_folder_list}

	rop_list=($(cat ${processed_rop_folder_list}))
    rop_info_file="${INSTALL_DIR}/.rop_info_file"

    if [[ ! -r ${rop_info_file} ]];then
        current_rop_count=0
    else
        previous_rop_count=$(cat ${rop_info_file})
        current_rop_count=$((${previous_rop_count} + 1))
        if [[ ${current_rop_count} -ge ${#rop_list[*]} ]];then
            current_rop_count=0
        fi
    fi
    echo ${current_rop_count} > ${rop_info_file}
    ropFolder=${rop_list[${current_rop_count}]}

    if [[ -z ${ropFolder} ]]; then
        log_it "Waiting for files to be processed. Please wait for next cycle to run"
        rm -rf ${targetDir}
        return 2
    else
        log_it "Rop folder to be linked : ${ropFolder}"
        sourceDir=${sourceDir}/${ropFolder}
        log_it "Temporary batch files directory is: $targetDir"

        if [[ "${instance_default}" -lt "${sim_count}" ]]; then
            start=0
            end=${instance_default}
            number_of_divisions=$((sim_count / instance_default))
            remainder=$((sim_count % instance_default))
            if [ ${remainder} -gt 0 ] ; then
                    number_of_divisions=$((number_of_divisions+1))
            fi
            log_it "Total number of groups : ${number_of_divisions}"
            for (( grp=0; grp < ${number_of_divisions}; grp++ ))
            do
                declare -a simulation_ids
                for (( instCount=${start}; instCount < ${end}; ++instCount ))
                do
                    simulation_ids+=(${sim_list_array[$instCount]})
                done
                log_it "Group ${grp} started"
                linkFilesForCTR simulation_ids[@]
                start=$((start+instance_default))
                end=$((end+instance_default))
                if [[ ${sim_count} -lt ${end} ]]; then
                        end=${sim_count}
                fi
                simulation_ids=()
            done
        else
            linkFilesForCTR sim_list_array[@]
        fi
    fi
}


##########################################################################################
#                                    Main Function                                       #
##########################################################################################
No_of_arg=$#
ValidateArguments $No_of_arg
rc=$?
if [ $rc -ne 0 ] ; then
        Usage
        log_it "ERROR: Error during validating command line."
        echo "Failed to link files"
        exit -1
fi

instance_default="40"
if [ $dataSource == "CTR" ]; then
        instance_default="5"
        baseOututDir=${3:-"/pms_tmpfs/SimName/FdnName/c/pm_data/"}
        setUpCTRFiles
elif [ $dataSource == "EBM" -o $dataSource == "SGSN" -o $dataSource == "MME" ]; then
        baseOututDir=${3:-"/netsim/netsim_dbdir/simdir/netsim/netsimdir/SimName/FdnName/fs/tmp/OMS_LOGS/ebs/ready"}
        number_of_scripts=${4:-40}
        linkFiles
elif [ $dataSource == "CTUM" ]; then
        baseOututDir=${3:-"/netsim/netsim_dbdir/simdir/netsim/netsimdir/SimName/FdnName/fs/tmp/OMS_LOGS/ctum/ready"}
        number_of_scripts=${4:-40}
        linkFiles
elif [ $dataSource == "LTEUETR" ]; then
        baseOututDir=${3:-"/netsim/netsim_dbdir/simdir/netsim/netsimdir/SimName/FdnName/fs/c/pm_data"}
        number_of_scripts=${4:-40}
        linkFiles
fi

rc=$?
if [ $rc -eq 2 ] ; then
        log_it "No files linked in this cycle"
        exit $rc
fi
if [ $rc -ne 0 ] ; then
        log_it "ERROR: Failed to link files"
        exit $rc
fi
