#!/bin/sh
###############################################################################
#############################################################################
# COPYRIGHT Ericsson 2020
#
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
###############################################################################
###############################################################################

#To fetch current path
CURRENT_DIR_PATH="`dirname \"$0\"`"

#Importing mounting configurations
#Keep the config.sh file in /netsim/EDE/ loc for first time of setup
source /netsim/EDE/config.sh

LOG_FILE="/netsim_users/pms/logs/remount"
log()
{
 echo "[${USER}] [`date`] - ${*}" >> ${LOG_FILE}
}

#This method is responsible for doing mounting on the netsim boxes
remount()
{
#check if mounting is already present or not
 if mount | grep EDE >> /dev/null 2>&1
then
 log "mounting is already Present"
elif mount ${IP_ADD}:${FILE_PATH} ${MOUNT_PATH} ;then
   if [[ $? == 0 ]];then
         log "Mounting done successfully "

   fi
else
log "There is issue with mounting"
exit 1
fi
 }

#This method is responsible for doing netsim_cfg changes to support high priority file based on node type
genstats_changes()
{
#To check netsim_cfg configurations are already there or not
if [[ ${NODE_TYPE} == 'ERBS' ]] &&  grep 'LTE_CELLTRACE_LIST="celltrace_1MB.bin.gz:1:3"' ${CFG_FILE} >>/dev/null
 then
 log "configuration is already updated for ${NODE_TYPE}"

 elif [[ ${NODE_TYPE} == 'MSRBS_V2' ]] &&  grep 'MSRBS_V2_LTE_CELLTRACE_LIST="celltrace_1MB.bin.gz:1:3"' ${CFG_FILE} >>/dev/null
then
 log "configuration is already updated for ${NODE_TYPE}"
else
#To take backup of netsim_cfg
cp ${CFG_FILE} ${BACKUP_CFG_FILE}
if [[ $? == 0 ]];then
log "netsim_cfg copied successfully"
else
log "ERROR ::Issue while copying file"
exit 1
fi
SUPPORTED_NE_TYPES="ERBS MSRBS_V2"

echo ${SUPPORTED_NE_TYPES} | grep ${NODE_TYPE} >> /dev/null

if [[ $? == 0 ]];then
   echo "INFO :: Started config changes for ${NODE_TYPE}"
   if [[ ${NODE_TYPE} == 'ERBS' ]] ; then
      sed -i "s/^LTE_CELLTRACE_LIST=\"celltrace_3MB.bin.gz:1:1 celltrace_1MB.bin.gz:1:3\"/LTE_CELLTRACE_LIST=\"celltrace_1MB.bin.gz:1:3\"/g" ${BACKUP_CFG_FILE}
      if [[ $? != 0 ]];then
         log "ERROR :: Issue while doing changes for ${NODE_TYPE} "
         exit 1
      fi
   elif [[ ${NODE_TYPE} == 'MSRBS_V2' ]] ; then
      sed -i "s/MSRBS_V2_LTE_CELLTRACE_LIST=\"celltrace_3MB.bin.gz:1:1 celltrace_1MB.bin.gz:1:3\"/MSRBS_V2_LTE_CELLTRACE_LIST=\"celltrace_1MB.bin.gz:1:3\"/g" ${BACKUP_CFG_FILE}
      if [[ $? != 0 ]];then
         log "ERROR :: Issue while doing config changes for ${NODE_TYPE} "
         exit 1
      fi
   fi
   echo "INFO :: config changes for ${NODE_TYPE} completed"
else
   log "WARNING :: ${NODE_TYPE} not supported"
   exit 1
fi

#to remove netsim_cfg
rm -f {CFG_FILE}
#command to rename backup file to netsim_cfg
mv ${BACKUP_CFG_FILE} ${CFG_FILE}
chown -R netsim:netsim ${CFG_FILE}

#to copy celltrace file
cp ${CELLTRACE_LOCTION} ${CEL_PATH}
if [[ $? == 0 ]];then
log "celltrace file copied successfully"
else
log "ERROR ::Issue while  coping celltrace file"
fi
fi
}

remount
genstats_changes

