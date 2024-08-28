package com.ericsson.cifwk.netsim;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;


import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import utils.GenericMethodUtils;
import utils.HostHandler;

import com.ericsson.cifwk.taf.annotations.Context;
import com.ericsson.cifwk.taf.annotations.Operator;
import com.ericsson.cifwk.taf.tools.cli.CLICommandHelper;

@Operator(context = Context.CLI)
public class MiniLinkUnitTestOperator implements UnitTestOperatorInterface {

	/** Taf command handler instance */
	private static CLICommandHelper cliCmdHelper;
	private static final String INFO = "INFO", ERROR = "ERROR";
	private static List<String> errFileList = new ArrayList<>();

	/** Logging utility */
	private static final Logger logger = LoggerFactory.getLogger(MiniLinkUnitTestOperator.class);

	public boolean initialise()
	{
		try 
		{
			cliCmdHelper = new CLICommandHelper(HostHandler.getTargetHost());
			return true;
		} 
		
		catch (final Exception e) 
		{
			GenericMethodUtils.printMessage("Error occured while initialising the TAF env.", ERROR);
			return false;
		}
	}

	

	public int verifyUnitTestScriptExecution(String test_id, String csvCommand) 
	{
		if (test_id == "minilink_indoor") 
		{
			generateIndoorCommand(test_id, csvCommand);
		}

		else 
		{
			generateOutdoorFiles(csvCommand, generateOutdoorCommand(test_id));
		}
		return 0;
	}

	
	
	public static void generateOutdoorFiles(String inputScript, String inputCommand) 
	{

		String exeCommand = inputScript + " " + inputCommand;

		String logs[] = cliCmdHelper.simpleExec(exeCommand).split("\r\n");

		validateGeneratedFiles(inputScript, inputCommand, logs);
	}

	
	public static void generateIndoorFiles(String[] argArray, String csvCommand, String fileType) 
	{
		Map<String, String> fileLocationMap = new HashMap<>();
		String[] exeCommand = new String[argArray.length];
		String filename = null;
		String filePath = null;

		for (int eleId = 0; eleId < argArray.length; eleId++) 
		{
			filePath = "/pms_tmpfs/" + argArray[eleId].split("::")[1].split(";")[0] + "/"
					+ argArray[eleId].split("::")[2].split(";")[0] + "/c/pm_data/";
			filename = argArray[eleId].split("::")[3].split(";")[0];
			fileLocationMap.put(filename, filePath);
			exeCommand[eleId] = "python " + csvCommand + " " + argArray[eleId];
		}

		GenericMethodUtils.printMessage("Genreting Mini-Link Indoor " + fileType + " PM files.", INFO);

		cliCmdHelper.simpleExec(exeCommand);

		String mlFilePath = null;

		for (String file : fileLocationMap.keySet()) 
		{
			mlFilePath = fileLocationMap.get(file);
			validatePmFileExistance(mlFilePath, file);
		}
	}

	
	
	public static void generateIndoorCommand(String test_id, String csvCommand) 
	{
		GenericMethodUtils.printMessage("Executing Mini-Link Indoor PM file generation test case.", INFO);
		String mlSampleTemplate = "/netsim_users/pms/minilink_templates";

		if (GenericMethodUtils.isFolderExists(mlSampleTemplate, cliCmdHelper).equalsIgnoreCase("FALSE")) 
		{
			GenericMethodUtils.printMessage("Mini-Link Sample Template folder " + mlSampleTemplate + " not found.", ERROR);
		}

		logger.info("Verifying the process of unit test execution.");
		if (test_id == "minilink_indoor") 
		{
			String[] nodeFamilyArr = { "CN510", "CN810", "CN210", "AMM6pD", "AMM20pB", "ML-LH", "ML-TN", "LH", "TN", "AMM2pB", "ML6651", "ML6691", "ML6692", "ML6693", "ML6366" };

			for (int rcGen = 1; rcGen <= nodeFamilyArr.length; rcGen++) 
			{
				GenericMethodUtils.printMessage("Creating commands for node family " + nodeFamilyArr[rcGen - 1] + " for ETHERNET PM file.", INFO);
				String stringRcId = String.valueOf(rcGen);
				String[] ethernetCommandArr = 
				{	
							"\"sim_name::ML6352-R2-7x2-CORE42;node_name::MLTN-5-4-1302;xfPMFileName::A20180307.1215+0200-1230+0200_TN-10-41-99-100_TN100_-_" 
								+ stringRcId + ".xml.gz;xfPMFileGranularityPeriod::1;rcID::" + stringRcId
								+ ";node_type::Mini-Link TN;fileToBeAssembled::" + nodeFamilyArr[rcGen - 1] + "\"",
						
							"\"sim_name::ML6352-R2-7x2-CORE42;node_name::MLTN-5-4-1302;xfPMFileName::A20180307.1215+0200-1215+0200_TN-10-41-99-100_TN100_-_"
								+ stringRcId + ".xml.gz;xfPMFileGranularityPeriod::2;rcID::" + stringRcId
								+ ";node_type::Mini-Link TN;fileToBeAssembled::" + nodeFamilyArr[rcGen - 1] + "\"",
						
							"\"sim_name::ML6352-R2-7x2-CORE42;node_name::MLTN-5-4-1302;xfPMFileName::C20180307.1215+0200-20180307.1230+0200_TN-10-41-99-100_TN100_-_"
								+ stringRcId + ".xml.gz;xfPMFileGranularityPeriod::1;rcID::" + stringRcId
								+ ";node_type::Mini-Link TN;fileToBeAssembled::" + nodeFamilyArr[rcGen - 1] + "\"",
							
							"\"sim_name::ML6352-R2-7x2-CORE42;node_name::MLTN-5-4-1302;xfPMFileName::C20180307.1215+0200-20180308.1215+0200_TN-10-41-99-100_TN100_-_"
								+ stringRcId + ".xml.gz;xfPMFileGranularityPeriod::2;rcID::" + stringRcId
								+ ";node_type::Mini-Link TN;fileToBeAssembled::" + nodeFamilyArr[rcGen - 1] + "\"" 
				};

				generateIndoorFiles(ethernetCommandArr, csvCommand, "ETHERNET");

			}

			for (int rcGen = 1; rcGen <= nodeFamilyArr.length; rcGen++) 
			{
				GenericMethodUtils.printMessage( "Creating commands for node family " + nodeFamilyArr[rcGen - 1] + " for SOAM PM file.", INFO);
				String stringRcId = String.valueOf(rcGen + 100);
				String[] soamCommandArr = 
				{
						"\"sim_name::ML6352-R2-7x2-CORE42;node_name::MLTN-5-4-1302;xfServiceOamPmFileName::A20180307.1215+0200-1230+0200_TN-10-41-99-100__-_"
								+ stringRcId + ".xml.gz;xfServiceOamPmFileGranularityPeriod::1;rcID::" + stringRcId
								+ ";node_type::Mini-Link PN;fileToBeAssembled::" + nodeFamilyArr[rcGen - 1] + "\"",
						
						"\"sim_name::ML6352-R2-7x2-CORE42;node_name::MLTN-5-4-1302;xfServiceOamPmFileName::A20180307.1215+0200-1215+0200_TN-10-41-99-100__-_"
								+ stringRcId + ".xml.gz;xfServiceOamPmFileGranularityPeriod::2;rcID::" + stringRcId
								+ ";node_type::Mini-Link PN;fileToBeAssembled::" + nodeFamilyArr[rcGen - 1] + "\"",
						
						"\"sim_name::ML6352-R2-7x2-CORE42;node_name::MLTN-5-4-1302;xfServiceOamPmFileName::C20180307.1215+0200-20180307.1230+0200_TN-10-41-99-100__-_"
								+ stringRcId + ".xml.gz;xfServiceOamPmFileGranularityPeriod::1;rcID::" + stringRcId
								+ ";node_type::Mini-Link PN;fileToBeAssembled::" + nodeFamilyArr[rcGen - 1] + "\"",
						
						"\"sim_name::ML6352-R2-7x2-CORE42;node_name::MLTN-5-4-1302;xfServiceOamPmFileName::C20180307.1215+0200-20180308.1215+0200_TN-10-41-99-100__-_"
								+ stringRcId + ".xml.gz;xfServiceOamPmFileGranularityPeriod::2;rcID::" + stringRcId
								+ ";node_type::Mini-Link PN;fileToBeAssembled::" + nodeFamilyArr[rcGen - 1] + "\"" 
				};
				generateIndoorFiles(soamCommandArr, csvCommand, "SOAM");
			}
		}
	}

	public static String generateOutdoorCommand(String test_id) 
	{
		errFileList.clear();
		GenericMethodUtils.printMessage("Executing " + test_id + " PM file generation test case.", INFO);
		String mlSampleTemplate = "/netsim_users/pms/minilink_templates";

		if (GenericMethodUtils.isFolderExists(mlSampleTemplate, cliCmdHelper).equalsIgnoreCase("FALSE")) 
		{
			GenericMethodUtils.printMessage("Mini-Link Sample Template folder " + mlSampleTemplate + " not found.", ERROR);
		}

		GenericMethodUtils.printMessage("MiniLink Templates found.", INFO);

		if (test_id == "fronthaul") 
		{
			return "\"sim_name::CORE-ST-FrontHaul-6392x5-CORE87;node_name::CORE87FrontHaul639201;node_type::Mini-Link FrontHaul;rcID::1;node_IP::10.155.71.197;node_category::outdoor\"";
		}

		else if (test_id == "outdoor") 
		{
			return "\"sim_name::CORE-FT-ML6693-1-4x2-CORE81;node_name::CORE42ML01;node_type::Mini-Link SW;rcID::1;node_IP::10.192.168.1;node_category::outdoor\"";
		}

		else if (test_id == "switch") 
		{
			return "\"sim_name::CORE-FT-Switch6391-2_9x2-CORE89;node_name::CORE42ML01;node_type::Mini-Link SW;rcID::1;node_IP::10.155.80.145;node_category::outdoor\"";
		}

		else 
		{
			return "Command could not be generated.";
		}
	}
	
	
	public static void validatePmFileExistance(String filePath, String fileName) 
	{
		if (GenericMethodUtils.isFolderExists(filePath, cliCmdHelper).equalsIgnoreCase("FALSE")) 
		{
			errFileList.add(filePath + fileName + " : PM file path does not exists.");
		} 
		
		else 
		{
			if (GenericMethodUtils.isFileExists(filePath + fileName, cliCmdHelper).equalsIgnoreCase("FALSE")) 
			{
				errFileList.add(filePath + fileName + " : PM file does not exists.");
			}
		}
	}
	

	public static void validateGeneratedFiles(String inputScript, String inputCommand, String logs[]) 
	{
		String pmFilePath = "/pms_tmpfs/" + inputCommand.split("::")[1].split(";")[0] + "/" + inputCommand.split("::")[2].split(";")[0] + "/c/pm_data/";

		GenericMethodUtils.printMessage("Genreting" + inputCommand.split("::")[1].split(";")[0] + " PM files.", INFO);

		List<String> fileNameList = new ArrayList<>();

		for (int i = 0; i < logs.length; i++) 
		{
			if (logs[i].contains("A type filename :") || logs[i].contains("C type filename :")) 
			{
				fileNameList.add(logs[i].split(":")[1].trim());
			}
		}

		String firstElement = fileNameList.get(0);

		String cmd = pmFilePath + firstElement;
		if (cmd.contains("A")) 
		{
			GenericMethodUtils.printMessage(cmd, INFO);
		}
		
		GenericMethodUtils.printMessage(cmd, INFO);

		for (String fileName : fileNameList) 
		{
			validatePmFileExistance(pmFilePath, fileName);
		}

		// Retrieval of BeginDate, EndDate, UserLabel & LocalDN from file name.
		String getFilenameBeginDate = "ls " + pmFilePath + " | grep -i 'A' | awk -F '[A.-]' '{print $2 $3 $4}' > FilenameBeginDate.txt";
		cliCmdHelper.execute(getFilenameBeginDate);

		String getFilenameEndDate = "ls " + pmFilePath	+ " | grep -i 'A' | awk -F '[A.-]' '{print $5 $6 $7}' > FilenameEndDate.txt";
		cliCmdHelper.execute(getFilenameEndDate);

		String getFilenameUserLabel = "ls " + pmFilePath + " | grep -i 'A' | awk -F '[_]' '{print $8}' > FilenameUserLabel.txt";
		cliCmdHelper.execute(getFilenameUserLabel);

		String getFilenameLocalDn = "ls " + pmFilePath + " | grep -i 'A' C > FilenameLocalDn.txt";
		cliCmdHelper.execute(getFilenameLocalDn);

		
		// Retrieval of BeginDate, EndDate, UserLabel & LocalDN from the internal content of the file.
		String getInternalBeginDate = "cat " + cmd + " | grep -i  'beginTime' | awk -F '[\"-]' '{print $2 $3 $4}' > InternalBeginDate.txt";
		cliCmdHelper.execute(getInternalBeginDate);

		String getInternalEndDate = "cat " + cmd + " | grep -i  'measCollec endTime' | awk -F '[\"=-]' '{print $3 $4 $5}' > InternalEndDate.txt";
		cliCmdHelper.execute(getInternalEndDate);

		String getInternalUserLabel = "cat " + cmd + " | grep -i 'userLabel' | awk -F '[\"]' '{print $2}' > InternalUserLabel.txt";
		cliCmdHelper.execute(getInternalUserLabel);

		String getInternalLocalDn = "cat" + cmd + " | grep -i 'localDn' | awk -F '[-_=\"]' '{print $4 $5 $6 $7 $8}' > InternalLocalDn.txt";
		cliCmdHelper.execute(getInternalLocalDn);

		
		// Changes to formatting for BeginDate and EndDate.
		String sedBeginDate = "sed -i -e 's/:/_/g' InternalBeginDate.txt";
		cliCmdHelper.execute(sedBeginDate);

		String sedEndDate = "sed -i -e 's/:/_/g' InternalEndDate.txt";
		cliCmdHelper.execute(sedEndDate);

		
		// Comparisons of filename data and internal data for each attribute.
		String compareBeginDates = "diff " + "./InternalBeginDate.txt " + "./FilenameBeginDate.txt";
		String outputBeginDates[] = cliCmdHelper.simpleExec(compareBeginDates).split("\r\n");

		String compareEndDates = "diff " + "./InternalEndDate.txt " + "./FilenameEndDate.txt";
		String outputEndDates[] = cliCmdHelper.simpleExec(compareEndDates).split("\r\n");

		String compareLocalDns = "diff " + "./InternalLocalDn.txt " + "./FilenameLocalDn.txt";
		String outputLocalDns[] = cliCmdHelper.simpleExec(compareLocalDns).split("\r\n");

		String compareUserLabels = "diff " + "./FilenameUserLabel.txt " + "./InternalUserLabel.txt";
		String outputUserLabels[] = cliCmdHelper.execute(compareUserLabels).split("\r\n");

		// If diff returns empty string, then the files are the same.
		if (outputLocalDns[0].equals("")) 
		{
			GenericMethodUtils.printMessage("Local DN has been correctly assigned", INFO);
		}

		if (outputUserLabels[0].equals("")) 
		{
			GenericMethodUtils.printMessage("User Label has been correctly assinged.", INFO);
		}

		if (outputBeginDates[0].equals("")) 
		{
			GenericMethodUtils.printMessage("Begin Date has been correctly assigned", INFO);
		}

		if (outputEndDates[0].equals("")) 
		{
			GenericMethodUtils.printMessage("End Date has been correctly assigned", INFO);
		}
	}


	@Override
	public int verifyScriptExecution(String command) {
		// TODO Auto-generated method stub
		return 0;
	}

}
