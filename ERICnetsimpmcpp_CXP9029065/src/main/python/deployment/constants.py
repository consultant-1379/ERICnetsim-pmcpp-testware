#!/usr/bin/python

class Constants(object):
    # ENM Config
    ENM_ID = 'ENM_ID'  # in netsim_cfg
    ENM_ID_LIST = 'ENM_ID_LIST'  # in config_map
    RELEASE = 'TYPE'
    # Unknown PMIC location structure
    PMIC_LOC = '/ericsson/pmic1/XML/'

    # Config file Config
    CONFIG_MAP_PATH = 'CONFIG_MAP_PATH'
    CONFIG_JSON = 'config.json'

    # Lock files
    DEPLOYING = '.DEPLOYING'
    SCALE_READY = '.SCALE_READY'
    SCALING = '.SCALING'

    # clean up
    FULL_CLEANUP = [DEPLOYING, SCALE_READY, SCALING]

    # network information json file, expected enm_id format i,e ENM_1, ENM_2,...
    ENM_NETWORK_JSON = '.simulated_network_<ENM_ID>.json'

    # locations
    NETSIM_CFG = '/netsim/netsim_cfg'
    PMS_LOG_LOC = '/netsim_users/pms/logs/'
    STARTED_NE_FILE = '/tmp/showstartednodes.txt'
    SIM_DATA_FILE = '/netsim/genstats/tmp/sim_data.txt'

    # Ne Support config
    SUPPORTED_NE_MAP = {'NRM6.3': ['GNODEBRADIO', 'PCC', 'PCG']}

    # NR ENM Config
    TOTAL_STARTED_NR_NES = 'TOTAL_STARTED_NR_NES'
    NR_SIMS_PER_ENM = 'NR_SIMS_PER_ENM'
    NR_NES_PER_SIM = 'NR_NES_PER_SIM'
    NR_MIM_RELEASE = 'NR_MIM_RELEASE'

    TOTAL_STARTED_PCC_NES = 'TOTAL_STARTED_PCC_NES'
    PCC_SIMS_PER_ENM = 'PCC_SIMS_PER_ENM'
    PCC_NES_PER_SIM = 'PCC_NES_PER_SIM'
    PCC_MIM_RELEASE = 'PCC_MIM_RELEASE'

    TOTAL_STARTED_PCG_NES = 'TOTAL_STARTED_PCG_NES'
    PCG_SIMS_PER_ENM = 'PCG_SIMS_PER_ENM'
    PCG_NES_PER_SIM = 'PCG_NES_PER_SIM'
    PCG_MIM_RELEASE = 'PCG_MIM_RELEASE'

    # Started node entry format
    START_NE_FORMAT = '    <NODE_NAME>         30.5.103.198 161 public v3+v2+v1 .128.0.0.193.1.30.5.103.198 mediation authpass privpass none none  [TLS] /netsim/netsimdir/<SIM_NAME>\n'
