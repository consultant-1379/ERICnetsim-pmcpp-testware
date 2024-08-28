#!/bin/bash
###############################################################################
###############################################################################
# COPYRIGHT Ericsson 2014                                                     #
#                                                                             #
# The copyright to the computer program(s) herein is the property of          #
# Ericsson Inc. The programs may be used and/or copied only with written      #
# permission from Ericsson Inc. or in accordance with the terms and           #
# conditions stipulated in the agreement/contract under which the             #
# program(s) have been supplied.                                              #
###############################################################################
###############################################################################

#delete.sh

#Initialize variables
#INSTALL_DIR=$(cd $(dirname "$0") && cd .. && pwd)
#LOG_DIR=${INSTALL_DIR}/logs
#LOG=$LOG_DIR/deleteEDEOutputFiles.log
#LOG=delete_logs/logs 
DATE=`date "+%Y_%m_%d_%H:%M:%S"`
INSTALL_DIR="$(cd $(dirname "$0") && pwd)"

if [ ! -d ${INSTALL_DIR}/logs/deleteFiles_log ] ; then
mkdir -p ${INSTALL_DIR}/logs/deleteFiles_log
fi
LOG="${INSTALL_DIR}/logs/deleteFiles_log/deleteFiles_${DATE}.$$.log"
deletion_flag=false

##########################################################################################################
# Function: Usage																						 #		
#																										 #	
# Description: This function display this tool usage information.										 #
##########################################################################################################
Usage(){
   echo ""
   echo "This script is used to delete previous generated files in FDN's on hourly basis.It will delete your previous generated files in FDN's with respect to current system time."
   echo "Usage: ./delete.sh <Path Upto FDN's> <Deletion Hours from 0 to 48>"
   echo "Script can be executed by adding crontab entry."
   echo "Crontab entry can be done by running command 'crontab -e'"
   echo ""
}
##########################################################################################################
# Function: ValidateArguments                                                                            #  
#                                                                                                        #
# Description: This function validates and parses the command line.                                      #
#                                                                                                        #
# Returns:                                                                                               #
#       0       Success                                                                                  #
#       1       Error                                                                                    #    
#                                                                                                        #
##########################################################################################################
ValidateArguments(){
   num_args=$1

   if [ $num_args -lt 2 ] ; then
     echo "ERROR: Invalid number of arguments specified." >> $LOG
     return 1 
   else
     echo "[`date`] : INFO: Validation successful." >> $LOG
	 deletion_flag=true
   fi
   return 0
}

##########################################################################################
##########################################################################################
#                                    Main Function                                       #
##########################################################################################
##########################################################################################

No_of_arg=$#
ValidateArguments $No_of_arg 
rc=$?
if [ $rc -ne 0 ] ; then
   Usage
   echo "ERROR: Failed to start stub." >> $LOG
   exit 1
fi

##########################################################################################
##########################################################################################
#                           Setting Java Execution Function                              #
##########################################################################################
##########################################################################################

if $deletion_flag; then 
	dirlist=$(find $1 -type l |grep "CellTrace")
	for dir in $dirlist
		do
	#if [[ -l $dir ]]; then
				filename=$(basename "$dir")
				extension="${filename##*.}"
				filename="${filename%.*}"
				if [ $extension == "gz" -o $extension == "bin" ]; then	
				      	fileDate=`echo $filename | cut -c2-9`
				      	fileStartTime=`echo $filename | cut -c11-14`
			            fileDateTime="$fileDate$fileStartTime"
					actualDATE=`TZ=GMT+$2 date +%Y%m%d%H%M`;
					
					if [ $actualDATE -ge $fileDateTime ]; then
					      #	echo "[`date`] : Filename : "$filename >> $LOG
					      #	echo "[`date`] : ActualDATE : "$actualDATE >> $LOG
					      #	echo "[`date`] : FileDateTime : "$fileDateTime >> $LOG
						echo "[`date`] : Deleting "$filename >> $LOG
						`rm -rf $dir &`
					fi	
				fi
	#		else
	#			ls
	#		fi		
		done
else
	echo "[`date`] : Deletion_flag is false.Please check input arguments." >> $LOG
fi	