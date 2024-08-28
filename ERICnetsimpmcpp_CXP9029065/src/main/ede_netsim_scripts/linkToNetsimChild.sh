#!/bin/bash
###############################################################################
###############################################################################
# COPYRIGHT Ericsson 2014
#
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
###############################################################################
###############################################################################

sourceDir=$1
baseOututDir=$2
targetDir=$3
LOG=$4
sim_name=$5
sourceBatchFileName=$6
total_files_linked=0

log_it(){
  echo `date "+%Y_%m_%d_%H:%M:%S"` $1 >> $LOG
}

ROP_PERIOD_SEC=900
#**************************** SET ROP TIMINIGS *****************************#
# Generate Epoch Seconds (UTC always)
# EDE always generate Files at End Time of ROP
current_epoch=$(date +%s)
start_epoch=$(($((${current_epoch}/${ROP_PERIOD_SEC}))*${ROP_PERIOD_SEC}))
end_epoch=$((${start_epoch}+${ROP_PERIOD_SEC}))


#*************************** PM FILE NAME ***********************************#
DATE=$(date -u -d @${start_epoch} +'%Y%m%d')
ROP_START_TIME=$(date -u -d @${start_epoch} +'%H%M')
ROP_END_TIME=$(date -u -d @${end_epoch} +'%H%M')


for fname in `cat $sourceBatchFileName`
	do
		link_Name="ADate.StartTime-EndTime_CellTrace_DUL1_RopIndex.bin.gz"
		fdn_name=`echo $fname | sed 's/^.*\(LTE[a-zA-Z0-9]\+\).*$/\1/'`
		#fdn_name=`echo $fname | awk -F"MeContext=" '{print $2}' | awk -F"_celltracefile" '{print $1}'`
		#if [[ $fdn_name == *[_]* ]];then  #It contains ieatnetsimv01
		#fdn_name=`echo $fdn_name | cut -d "_" -f2`
		#fi
		#sim_name=`echo $fdn_name | awk -F"ERBS" '{print $1}'`
		#sim_name=`echo $fdn_name | sed 's/^.*\(LTE[0-9]\+\).*$/\1/'`
		output_dir="${baseOututDir/SimName/$sim_name}"
		output_dir="${output_dir/FdnName/$fdn_name}"
		if [ -d "$output_dir" ]; then
			file_date=${fname:1:8}
			#time=`echo $fname | sed -e "s/.*${file_date}"."\(.*\)_SubNetwork.*/\1/"`
			#start_time=`echo $time | cut -d "-" -f1`
			#start_time=${start_time:0:4}
			#end_time=`echo $time | cut -d "-" -f2`
			#end_time=${end_time:0:4}
			if [[ "$fname" == *_celltracefile*_1* ]]; then
                            rop_index=1
                        else
                            rop_index=3
                        fi
			link_Name="${link_Name/Date/$DATE}"
			link_Name="${link_Name/StartTime/$ROP_START_TIME}"
			link_Name="${link_Name/EndTime/$ROP_END_TIME}"
			link_Name="${link_Name/RopIndex/$rop_index}"
			final_link_name=$output_dir$"/"$link_Name
			final_source_name=$sourceDir"/"$fname
			ln -s $final_source_name $final_link_name
			rc=$?
			if [ $rc -ne 0 ] ; then
				if [ $rc -eq 2 ] ; then
					log_it "INFO: File exists: $final_link_name"
				else
					log_it "ERROR: Failed to link $final_link_name"
				fi
			else
				total_files_linked=$((total_files_linked+1))
			fi
		fi
done

log_it "Completed script for $sim_name with total links $total_files_linked"
