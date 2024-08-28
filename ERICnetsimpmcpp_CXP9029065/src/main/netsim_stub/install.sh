#!/bin/bash

################################################################################
# COPYRIGHT Ericsson 2018
#
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
################################################################################

###################################################
# Version no    :  NSS 18.1 
# Purpose       :  The purpose of this script to install all the modeules of netsim_stub 
# Jira No       :  EQEV-47447
# Gerrit Link   :  https://gerrit.ericsson.se/#/c/3311326/
# Description   :  Created the script as a part of the netsim stub
# Date          :  08/02/2018
# Last Modified :  sardana.bhav@tcs.com 
####################################################

# ********************************************************************
#
#   Command Section
#
# ********************************************************************
NSLOOKUP=/usr/bin/nslookup
AWK=/usr/bin/awk
BASENAME=/bin/basename
BC=/usr/bin/bc
CAT=/bin/cat
CHMOD=/bin/chmod
CHOWN=/bin/chown
CLEAR=/usr/bin/clear
CMP=/usr/bin/cmp
CP=/bin/cp
CUT=/usr/bin/cut
DATE=/bin/date
DF=/bin/df
DIRNAME=/usr/bin/dirname
DOMAINNAME=/bin/domainname
ECHO=/bin/echo
EGREP=/bin/egrep
EJECT=usr/sbin/eject
ENV=/bin/env
EXPR=/usr/bin/expr
FUSER=/sbin/fuser
GETENT=/usr/bin/getent
GETTEXT=/bin/gettext
GREP=/bin/grep
GTAR=/bin/gtar
ZCAT=/bin/zcat
HEAD=/usr/bin/head
HOSTID=/bin/hostid
HOSTNAME=/usr/bin/hostname
ID=/usr/bin/id
INIT=/sbin/init
LS=/bin/ls
MKDIR=/bin/mkdir
MORE=/bin/more
MOUNT=/bin/mount
MYHOSTNAME=/bin/hostname
MV=/bin/mv
PGREP=/usr/bin/pgrep
PING=/bin/ping
PS=/bin/ps
PWD=/bin/pwd
RM=/bin/rm
RCP=/usr/bin/rcp
RSH=/usr/bin/rsh
SCP=/usr/bin/scp
SED=/bin/sed
SLEEP=/bin/sleep
SORT=/bin/sort
SU=/bin/su
SYNC=/bin/sync
TAIL=/usr/bin/tail
TEE=/usr/bin/tee
TEST=/usr/bin/test
TOUCH=/bin/touch
TPUT=/usr/bin/tput
TR=/usr/bin/tr
UMOUNT=/bin/umount
UNAME=/bin/uname
UNIQ=/usr/bin/uniq
VOLD=/usr/sbin/vold
WC=/usr/bin/wc


# ********************************************************************
#
#       Configuration Section
#
# ********************************************************************

# Default user
DEFAULT_USER=root
LOGFILE=/netsim_users/pms/logs/netsim_stub_logs/installation.log

# ********************************************************************
#
#       Pre-execution Operations
#
# ********************************************************************


# ********************************************************************
#
#   functions
#
# ********************************************************************

### Function: abort_script ###
#
#   This will is called if the script is aborted thru an error
#   error signal sent by the kernel such as CTRL-C or if a serious
#   error is encountered during runtime
#
# Arguments:
#       $1 - Error message from part of program (Not always used)
# Return Values:
#       none
abort_script()
{
clean_up
_err_time_=`$DATE '+%Y-%b-%d_%H.%M.%S'`
_err_msg_=$1

if [ ${LOGFILE} ]; then
    log_msg -s "ERROR: ${_err_msg_}" -l "${LOGFILE}" -t
else
    log_msg -s "ERROR: ${_err_msg_}" -t
fi


if [ $2 ]; then
    ${2}
else
   exit 1
fi
}

### Function: log_msg ###
#
# I will create the function log if one does not already exist
# This allows user to have his/her own log function and still
# work with the commmon functions
#
# Arguments:
#       -l) : File to be logged to
#               -h) : Print the message as a header
#       -q) : don't echo the text, just tee it
#       -s) : Text/message to be logged
#               -t) : Prints the current time as part of the message
# Return Values:
#       0 : Success
#       1 : Error
log_msg()
{
local logfile quiet outstr header msg_time

while [ -n "$1" ]; do
    case $1 in
        -l)     logfile=$2
                shift 2
                ;;
        -h)     header=-h
                shift 1
                ;;
        -q)     quiet=-q
                shift 1
                ;;
        -s)     outstr=$2
                shift 2
                ;;
        -t)     msg_time=-t
                shift 1
                ;;
        *)      return 1
                ;;
    esac
done

if [ ! "${outstr}" ]; then
    return 1
fi

local run_time=`$DATE '+%Y-%m-%d_%H.%M.%S'`
if [ "${msg_time}" ]; then
    outstr="${run_time} - ${outstr}"
fi

if [ "${header}" ]; then
        # Print the message as a header. This will
        # pad the string to a defined length and
        # add a prefix and postfix tag (<=== and ===>)
        if [ "${logfile}" ]; then
            if [ ! "${quiet}" ]; then
                $ECHO -e "${outstr}" | $AWK '
                        {
                                n1=length($0)
                                n2=36-n1/2-n1%2
                                n3=34-n1/2
                                printf("\n\n")
                                for ( n=1; n<n2; n++)
                                        printf("=")
                                        printf("=< %s >=",$ 0)
                                        for ( n=1; n<n3 ;n++ )
                                                printf("=")
                                                printf("\n\n")
                        }' | $TEE -a ${logfile}
            else
                $ECHO -e "${outstr}" | $AWK '
                        {
                                n1=length($0)
                                n2=36-n1/2-n1%2
                                n3=34-n1/2
                                printf("\n\n")
                                for ( n=1; n<n2; n++)
                                        printf("=")
                                        printf("=< %s >=",$ 0)
                                        for ( n=1; n<n3 ;n++ )
                                                printf("=")
                                                printf("\n\n")
                        }' >> ${logfile}
            fi
        else
            if [ ! "${quiet}" ]; then
                $ECHO -e "${outstr}" | $AWK '
                        {
                                n1=length($0)
                                n2=36-n1/2-n1%2
                                n3=34-n1/2
                                printf("\n\n")
                                for ( n=1; n<n2; n++)
                                        printf("=")
                                        printf("=< %s >=",$ 0)
                                        for ( n=1; n<n3 ;n++ )
                                                printf("=")
                                                printf("\n\n")
                        }'
            fi
        fi
else
        # Simply print the message
        if [ "${logfile}" ]; then
            if [ ! "${quiet}" ]; then
                $ECHO "${outstr}" |$TEE -a ${logfile}
            else
                $ECHO "${outstr}" >> ${logfile}
            fi
        else
            if [ ! "${quiet}" ]; then
                $ECHO "${outstr}"
            fi
        fi
fi
}


### Function: setup_env ###
#
# Set up environment variables for script.
#
# Arguments:
#   none
# Return Values:
#   none
setup_env()
{

log_msg -s "Setting up environment for installation of netsim stub package" -l "${LOGFILE}" -t 
WORKING_DIR=`$DIRNAME $0`
BASE_DIR=/netsim
PMS_DIR=/pms_tmpfs
TOPOLOGY_OP_DIR=/eniq
PM_OP_DIR=/ossrc
BIN_DIR=${BASE_DIR}/bin
ETC_DIR=${BASE_DIR}/etc
LIB_DIR=${BASE_DIR}/lib
INST_DIR=${BASE_DIR}/inst
NETSIM_DIR=${BASE_DIR}/netsimdir
DB_DIR=${BASE_DIR}/netsim_dbdir/simdir/netsim/netsimdir/
ENVIRONMENT=${ETC_DIR}/environment
USER_INPUT_XML=${ETC_DIR}/user_input.xml
NETYPES=${ETC_DIR}/netypes.txt
LINK_DIR=/ossrc/data/pmMediation/pmData/
MOUNT_PATH=/eniq/data/importdata/
ENIQ_STATS_CFG=/netsim_users/pms/bin/eniq_stats_cfg
EUTRANCELLDATAFILE=EUtranCellData.txt
TOPOLOGYFILE=TopologyData.txt
MO_CSV_FILE=/netsim_users/reference_files/OSS/mo_cfg_oss.csv
GENERATE_EUTRANDATA=${BIN_DIR}/generateEutranDataFile.py
TMPFS_DIR=/pms_tmpfs/
JAVA_LINK=/netsim/inst/platf_indep_java/linux64/jre/bin/java
USER_NAME=netsim
UPDATE_STATS_CFG=${BIN_DIR}/update_stats_cfg.py
GENSTATS_SCRIPT=/netsim_users/pms/bin/genStats
USER_INPUT_XSD=${WORKING_DIR}/etc/user_input.xsd

DIRECTORY_ARRAY=("/netsim/genstats/logs/rollout_console/"  "/netsim/netsimdir/"  "/netsim/netsim_dbdir/simdir/netsim/netsimdir/"  "/netsim/genstats/tmp/"  "/netsim/inst/zzzuserinstallation/mim_files/"  "/netsim/inst/zzzuserinstallation/ecim_pm_mibs/"  "/netsim/bin/"  "/netsim/etc/"  "/netsim/inst/platf_indep_java/linux64/jre/bin" "/eniq/" "/ossrc/data/pms/segment1/" "/netsim/etc/csv/" "/netsim_users/pms/logs/netsim_stub_logs/")

CLEANUP_ARRAY=("${BASE_DIR}/*" "${PMS_DIR}/" "${TOPOLOGY_OP_DIR}/", "${PM_OP_DIR}/")

SHAREDIRECTORY_ARRAY=("/ossrc" "/eniq")

LOGFILE=/netsim_users/pms/logs/netsim_stub_logs/installation.log

GENERATEEUTRANDATA_LOGFILE=/netsim_users/pms/logs/netsim_stub_logs/generateEutranDataFile.py.log
}
### Function: cleanup_prev_run ###
#
# Start the ENIQ services in the deployment
#
# Arguments:
#       none
# Return Values:
#       none
cleanup_prev_run()
{
#remove data from previous rollout
log_msg -s "removing data from previous rollout" -l "${LOGFILE}" -t 
for dir in ${CLEANUP_ARRAY[@]}
do
    ${RM} -rf ${dir}
done
}

### Function: create_base_dirs ###
#
# Start the ENIQ services in the deployment
#
# Arguments:
#       none
# Return Values:
#       none
create_base_dirs()
{
#create basic directory structure for netsim
log_msg -s "creating directory structure to enable genstats" -l "${LOGFILE}" -t 
for dir in ${DIRECTORY_ARRAY[@]}
do
    ${MKDIR} -p ${dir}
done
}

### Function: vallidate_xml ###
#
# Start the ENIQ services in the deployment
#
# Arguments:
#       $1: schema_file
#       $2: input_xml_file
# Return Values:
#       none
vallidate_xml()
{
schema_file=$1
input_xml_file=$2

#format user_input.xml file
log_msg -s "vallidating the network xml file (user_input.xml)" -l "${LOGFILE}" -t 
xmllint --noout --schema ${schema_file} ${input_xml_file}
if [ $? -ne 0 ]
then
    _err_msg_="user_input.xml not consistant."
    abort_script "${_err_msg_}"
else
    xmllint --format ${input_xml_file} > ${USER_INPUT_XML}
fi
}

### Function: copy_scripts ###
#  
# Copying the scripts into respective directrories ###
#
# Return Values:
#       none
copy_scripts()
{
log_msg -s "copying netsim stub package to desired location" -l "${LOGFILE}" -t -q
${CP} ${WORKING_DIR}/bin/* ${BIN_DIR}/
if [ $? -ne 0 ]; then
    _err_msg_="could not copy files from ${WORKING_DIR}/bin/ to ${BIN_DIR}/"
    abort_script "${_err_msg_}"
fi
${CP} ${WORKING_DIR}/commands/* ${BIN_DIR}/
if [ $? -ne 0 ]; then
    _err_msg_="could not copy files from ${WORKING_DIR}/commands/ to ${BIN_DIR}/"
    abort_script "${_err_msg_}"
fi
${CP} ${WORKING_DIR}/etc/* ${ETC_DIR}/
if [ $? -ne 0 ]; then
    _err_msg_="could not copy files from ${WORKING_DIR}/etc/ to ${ETC_DIR}/"
    abort_script "${_err_msg_}"
fi
${CP} ${WORKING_DIR}/shell/* ${INST_DIR}/
if [ $? -ne 0 ]; then
    _err_msg_="could not copy files from ${WORKING_DIR}/shell/ to ${INST_DIR}/"
    abort_script "${_err_msg_}"
fi
${CP} /netsim_users/pms/bin/eniq_stats_cfg ${BIN_DIR}/eniq_stats_cfg.py
if [ $? -ne 0 ]; then
    _err_msg_="could not copy /netsim_users/pms/bin/eniq_stats_cfg to ${BIN_DIR}"
    abort_script "${_err_msg_}"
fi

}
### Function: create_output_dirs ###
#
# Return Values:
#       none
create_output_dirs()
{
log_msg -s "creating output directories" -l "${LOGFILE}" -t
user_input=$1
if [ -e ${user_input} ]; then
    OUTPUT=`python ${BIN_DIR}/createOutputdirectory.py ${user_input} 2>&1`
	if [ "${OUTPUT}" !=  "0" ]; then
        log_msg -s "Output directory for this ${OUTPUT} are not created.PM files will not be created for these simulations" -l "${LOGFILE}" -t	
	fi
else
    _err_msg_="Does not find user_input.xml"
    abort_script "${_err_msg_}"
fi

}

### Function: generate_eutrancell_data ###
#
# Return Values:
#       none
generate_eutrancell_data()
{
log_msg -s "GeneratingEutran Cell data for LTE simulations" -l "${LOGFILE}" -t
if [ -e ${GENERATE_EUTRANDATA}  ]; then
    su - netsim -c "/usr/local/bin/python2.7 ${GENERATE_EUTRANDATA}"
    $GREP -wi "error" ${GENERATEEUTRANDATA_LOGFILE} > /dev/null
    if [ $? -eq 0 ]; then
       _err_msg_="Eutran data not generated properly. check log file ${GENERATEEUTRANDATA_LOGFILE}"
       abort_script "${_err_msg_}"
    fi
else
    _err_msg_="${GENERATE_EUTRANDATA}  is not present in the directory"
    abort_script "${_err_msg_}" 
fi

}

### Function: update_eniqstats_cfg ###
#
# Return Values:
#       none
update_eniqstats_cfg()
{
log_msg -s "Updating eniqstats_cfg file" -l "${LOGFILE}" -t
if [ -e ${UPDATE_STATS_CFG}  ]; then
    su - netsim -c "python  ${UPDATE_STATS_CFG}"
else
    _err_msg_="${UPDATE_STATS_CFG} is not present in the directory"
    abort_script "${_err_msg_}"
fi

}
### Function: clean_up ###
#
# Return Values:
#       none
clean_up()
{
log_msg -s "Cleaning the Directory which are not required" -l "${LOGFILE}" -t
$RM -rf /tmp/NodeMOMs.zip
$RM -rf /tmp/NodeMOMs
$RM -rf /tmp/mounted_dirs
$RM -rf /tmp/hosts_tmp
}


### Function: change_permissions ###
#
# Return Values:
#       none
change_permissions()
{
log_msg -s "changing permissions to netsim user" -l "${LOGFILE}" -t
$CHOWN -R netsim:netsim ${BASE_DIR} ${PMS_DIR} ${TOPOLOGY_OP_DIR} ${PM_OP_DIR} ${RPM_DIR}
$CHMOD -R 755 ${BASE_DIR} ${PMS_DIR} 
$CHMOD -R 777 ${TOPOLOGY_OP_DIR} ${PM_OP_DIR}
}

### Function: unmount_dirs ###
#
# Return Values:
#       none
unmount_dirs()
{
log_msg -s "unmounting pms_tmpfs dir if mounted" -l "${LOGFILE}" -t
$MOUNT | $GREP pms_tmpfs | $CUT -d" " -f3 > /tmp/mounted_dirs
while read line
do
    $UMOUNT -f $line
done </tmp/mounted_dirs

}

### Function: add_user ###
#
# Arguments:
#       $1: user name
#       $2: password
#       $3: group
#       $4: directory
# Return Values:
#       none
add_user()
{

log_msg -s "adding user" -l "${LOGFILE}" -t
_user_=$1
_password_=$2
_group_=$3
_directory_=$4
groupadd -f ${_group_}
useradd  -g ${_group_} -d ${_directory_} ${_user_}
if [ $? -ne 0 -a $? -ne 9 ]; then
    _err_msg_="could not create user netsim. exiting"
    abort_script "${_err_msg_}"
fi
$ECHO ${_password_} | passwd ${_user_} --stdin > /dev/null
}

### Function: setup_rsh ###
#
# Arguments:
#       $1: server name
# Return Values:
#       none
setup_rsh()
{

log_msg -s "setting up rsh" -l "${LOGFILE}" -t
_hostfile_=/etc/hosts
_rsh_file_=/etc/pam.d/rsh
_eqiv_file_=/etc/hosts.equiv
_securetty_file_=/etc/securetty
_rsh_file_xinetd_=/etc/xinetd.d/rsh
_rhosts_file_=~/.rhosts
_ip_file_=/exthostname/IP

HOSTNAME=`hostname`
HOST=${HOSTNAME}

if [[ ${HOSTNAME} == *"netsim"* ]]; then
    HOST="netsim.vts.com"
fi

$NSLOOKUP ${HOST} > /dev/null
if [ $? -ne 0 ];then
    _err_msg_="could not find IP address. Exiting"
    abort_script "${_err_msg_}"
else
   IP=`$NSLOOKUP ${HOST} | $GREP "Address" | $TAIL -1 | $CUT -d' ' -f2`
fi

if [ -s ${_ip_file_} ]; then
    IP=`$CAT ${_ip_file_}`
fi

$SED -i '/disable/s/.*/        disable = no/' ${_rsh_file_xinetd_}

$GREP "$IP netsim" ${_hostfile_} > /dev/null
if [ $? -ne 0 ];then
    $SED '/netsim/d' ${_hostfile_} > /tmp/hosts_tmp
    $ECHO "$IP netsim"  >> /tmp/hosts_tmp
    $MV /tmp/hosts_tmp ${_hostfile_}
fi

$ECHO "+ +" > ${_eqiv_file_}

$ECHO "+ +" > ${_rhosts_file_}

$CHMOD 600 ${_hostfile_}
$CHMOD 600 ${_rhosts_file_}
$CHMOD 600 ${_eqiv_file_}

$GREP "rsh" "${_securetty_file_}"  > /dev/null
if [ $? -ne 0 ];then
    $ECHO "rsh" >> "${_securetty_file_}"
fi

$CAT "${_rsh_file_}" | $GREP "pam_rhosts.so" | $GREP "sufficient"  > /dev/null
if [ $? -ne 0 ];then
    $SED -i '/pam_rhosts\.so/s/required/sufficient/' "${_rsh_file_}"
fi

chkconfig rsh on
/etc/init.d/xinetd restart > /dev/null

rsh -l netsim netsim ls > /dev/null
if [ $? -ne 0 ]; then
    _err_msg_="rsh not configured properly. Exiting installation"
    abort_script "${_err_msg_}"
fi

rsh -l root netsim ls > /dev/null
if [ $? -ne 0 ]; then
    _err_msg_="rsh not configured properly. Exiting installation"
    abort_script "${_err_msg_}"
fi

}

### Function: share_outputdirectory ###
#
# Check Input Params
#
# Arguments:
#       none
# Return Values:
#       none

share_outputdirectory()
{
log_msg -s "Sharing /ossrc and /eniq" -l "${LOGFILE}" -t

_export_file_=/etc/exports
for dir in ${SHAREDIRECTORY_ARRAY}
do 
    $GREP -w ${dir} "${_export_file_}" > /dev/null
    if [ $? -ne 0 ];then
       $ECHO  "${dir} *(rw,sync)" >> "${_export_file_}"
    fi
done

/etc/init.d/nfs restart > /dev/null
if [ $? -ne 0 ];then
    log_msg -s "could not restart nfs. /ossrc and /eniq will not be shared. Please share it manually" -l "${LOGFILE}" -t
fi

}

### Function: extract_mom_files ###
#
# Check Input Params
#
# Arguments:
#       none
# Return Values:
#       none
extract_mom_files()
{
 
log_msg -s "Extracting Node MOM files" -l "${LOGFILE}" -t
unzip /tmp/NodeMOMs.zip -d /tmp/ > /dev/null
if [ $? -ne 0 ]; then
    _err_msg_="Could not extract NodeMOMs"
    abort_script "${_err_msg_}"
fi
unzip -j /tmp/NodeMOMs/mim_files.zip -d /netsim/inst/zzzuserinstallation/mim_files/ > /dev/null
if [ $? -ne 0 ]; then
    _err_msg_="Could not extract MIM files"
    abort_script "${_err_msg_}"
fi
unzip -j /tmp/NodeMOMs/ecim_pm_mibs.zip -d /netsim/inst/zzzuserinstallation/ecim_pm_mibs/ > /dev/null
if [ $? -ne 0 ]; then
    _err_msg_="Could not extract MIB Files"
    abort_script "${_err_msg_}"
fi

}

### Function: check_params ###
#
# Check Input Params
#
# Arguments:
#       none
# Return Values:
#       none
check_params()
{
# Check that we got the required params
if [ ! ${DEPLOYMENT_TYPE} -o ! ${NETWORK_XML_PATH} ]; then
    usage_msg
    exit 1
fi

}



# Check/Create Logfile
#
# Arguments:
#   none
# Return Values:
#   none
chk_create_logfile()
{


$MKDIR -p `$DIRNAME ${LOGFILE}`
if [ $? -ne 0 ]; then
     _err_msg_="Could not create directory `$DIRNAME ${LOGFILE}`"
     abort_script $_err_msg_
fi

$TOUCH -a ${LOGFILE}

if [ $? -ne 0 ]; then
    _err_msg_="Could not write to file ${LOGFILE}"
    abort_script $_err_msg_
fi

}


### Function: get_absolute_path ###
#
# Determine absolute path to software
#
# Arguments:
#   none
# Return Values:
#   none
get_absolute_path()
{
_dir_=`$DIRNAME $0`
SCRIPTHOME=`cd $_dir_ 2>/dev/null && pwd || $${ECHO} $_dir_`
}


### Function: usage_msg ###
#
#   Print out the usage message
#
# Arguments:
#   none
# Return Values:
#   none
usage_msg()
{
$CLEAR
$ECHO "Usage: `$BASENAME $0` -b <deployment_type> -n <network_xml_location> 

options: 

-d  : This is mandatory parameter which defines the what type deployment
      you had selected .Ex NSS 
      
      
-n  : This is mandatory parameter which tell user about where the network
      configuration file is kept. By default it is /var/tmp/.  
	 
"

}

# ********************************************************************
#
#   Main body of program
#
# ********************************************************************
#

while getopts ":d:n:" arg; do
  case $arg in
    d) DEPLOYMENT_TYPE=$OPTARG
       ;;
    n) NETWORK_XML_PATH=$OPTARG
       ;;
    \?) echo $arg
       usage_msg
       exit 1
       ;;
  esac
done
shift `expr $OPTIND - 1`

# Check Input Params
check_params

# create and check log file
chk_create_logfile

case ${DEPLOYMENT_TYPE} in
  NSS) INPUT_XML=${NETWORK_XML_PATH}/user_input.xml
     ;;
  NRM) INPUT_XML=
     ;;
     *) abort_script "Please check deployment type"
     ;;
esac

crontab -u netsim -l | grep -vi ede | crontab -u netsim -
# Setup up path environment etc
setup_env

unmount_dirs
cleanup_prev_run

create_base_dirs

vallidate_xml ${USER_INPUT_XSD} ${INPUT_XML}

copy_scripts

add_user netsim netsim netsim /netsim

$CHOWN -R netsim:netsim `$DIRNAME ${LOGFILE}`

create_output_dirs ${USER_INPUT_XML}

extract_mom_files

ls -l /usr/sbin/tc > /dev/null
if [ $? -ne 0 ]; then
    ln -s /sbin/tc /usr/sbin/tc
    if [ $? -ne 0 ];then
       log_msg -s "could not create /usr/sbin/tc" -l "${LOGFILE}" -t
    fi
fi

ls -l ${JAVA_LINK} 2&>1 /dev/null
if [ $? -ne 0 ]; then
     ln -s /usr/bin/java ${JAVA_LINK}
     if [ $? -ne 0 ];then
        log_msg -s "could not create /usr/bin/java" -l "${LOGFILE}" -t
     fi
fi

change_permissions


setup_rsh ${SERVER}

generate_eutrancell_data

update_eniqstats_cfg

share_outputdirectory

su - netsim -c "$ECHO '.show started' | /netsim/inst/netsim_pipe > /tmp/.showstartednodes.txt"
su - netsim -c "$CP /tmp/.showstartednodes.txt /tmp/showstartednodes.txt"

clean_up
