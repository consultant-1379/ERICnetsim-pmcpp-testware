/*------------------------------------------------------------------------------
 *******************************************************************************
 * COPYRIGHT Ericsson 2018
 *
 * The copyright to the computer program(s) herein is the property of
 * Ericsson Inc. The programs may be used and/or copied only with written
 * permission from Ericsson Inc. or in accordance with the terms and
 * conditions stipulated in the agreement/contract under which the
 * program(s) have been supplied.
 *******************************************************************************
 *----------------------------------------------------------------------------*/
package com.ericsson.cifwk.netsim;

import java.util.ArrayList;
import com.ericsson.cifwk.taf.annotations.Context;
import com.ericsson.cifwk.taf.annotations.Operator;
import com.ericsson.cifwk.taf.data.User;
import com.ericsson.cifwk.taf.data.UserType;
import com.ericsson.cifwk.taf.tools.cli.CLICommandHelper;
import utils.GenericMethodUtils;
import utils.HostHandler;
import utils.DataAndStringConstants;

@Operator(context = Context.CLI)
public class GenericTestsOperator implements GenericTestsOperatorInterface {
	/** Taf command handler instance */
	private static CLICommandHelper cliCmdHelper;

	public boolean initialise() {
		try {
			cliCmdHelper = new CLICommandHelper(HostHandler.getTargetHost());
			return true;
		} catch (final Exception e) {
			GenericMethodUtils.printMessage("Error occured while initialising the TAF env.",
					DataAndStringConstants.ERROR);
			return false;
		}
	}

	public int verifyGenericTestScriptExecution(String testcase_Id, String simType, String nodeType,
			String subscription, String behaviour, String expectedOutput) {
		String[] sims = getSimList(simType, nodeType, behaviour);
		if (sims == null) {
			GenericMethodUtils.printMessage("SIMS are not installed or deployed on NETSIM box",
					DataAndStringConstants.WARN);
			return 0;
		}

		String[] typeOfFileStrings;
		ArrayList<Integer> exitCodes = new ArrayList<>();

		if (simType.contains(DataAndStringConstants.LTE)) {
			typeOfFileStrings = new String[] { "CellTrace_DUL1_3", "CellTrace_DUL1_1" };
		} else if (simType.contains(DataAndStringConstants.EPG)) {
			typeOfFileStrings = new String[] { "node", "pgw", "sgw" };
		} else if (simType.contains(DataAndStringConstants.RNC)) {
			typeOfFileStrings = new String[] { "CTR", "UETR" };
		} else {
			typeOfFileStrings = new String[] {};
		}

		for (String sim : sims) {
			sim = sim.trim();
			GenericMethodUtils.printMessage("Simulation being processed: " + sim, DataAndStringConstants.INFO);
			String isSimStarted = cliCmdHelper.simpleExec("cat /tmp/showstartednodes.txt | grep " + sim).trim();
			if (!isSimStarted.isEmpty()) {
				String finalLocation = getFinalLoc(sim, simType, nodeType, subscription, behaviour);
				String nodeList = cliCmdHelper
						.simpleExec("ls ".concat(DataAndStringConstants.NETSIM_DBDIR_PATH).concat(sim)).trim();
				String[] nodes = nodeList.split("\\s+");
				for (String node : nodes) {
					node = node.trim();
					String dirPath = DataAndStringConstants.NETSIM_DBDIR_PATH.concat(sim).concat("/").concat(node);
					String expectedFilePath = dirPath.concat(finalLocation);
					if (subscription.equalsIgnoreCase(DataAndStringConstants.STATS)) {
						String year = cliCmdHelper.simpleExec(DataAndStringConstants.EXTRACT_YEAR_CMD).trim();
						String fileWithPath = cliCmdHelper
								.simpleExec("find " + dirPath + " -type f -name A" + year + "* | sort | head -1")
								.trim();
						if (fileWithPath == null || fileWithPath.isEmpty()) {
							GenericMethodUtils.printMessage(
									"Output file is not getting generated for node " + node + " of simulation : " + sim,
									DataAndStringConstants.ERROR);
							return 1;
						}
						String actualFilePath = fileWithPath
								.replace(fileWithPath.split(DataAndStringConstants.FRWD_SLASH)[fileWithPath.split(DataAndStringConstants.FRWD_SLASH).length - 1], "");
						String latestPmFile = cliCmdHelper
								.simpleExec("ls -lrt " + actualFilePath + " | grep -v ^d | grep -v ^l | tail -1 ")
								.trim().split("\\s+")[8];
						exitCodes.add(compareFileInfo(testcase_Id, sim, node, actualFilePath, expectedFilePath,
								latestPmFile, expectedOutput));
					} else if (subscription.equalsIgnoreCase(DataAndStringConstants.EVENTS)) {
						if (typeOfFileStrings.length == 0) {
							GenericMethodUtils.printMessage(
									" No filetype is defined for Events subscription.Please add if block for your node's events subscription. ",
									DataAndStringConstants.WARN);
							return 0;
						}

						// Special handling for Dual BB & MultiStandard nodes
						if (simType.contains(DataAndStringConstants.LTE)) {
							if (!cliCmdHelper.simpleExec("cat " + DataAndStringConstants.SIM_INFO_FILE + " | grep "
									+ sim.split(DataAndStringConstants.SEPARATOR)[sim.split(DataAndStringConstants.SEPARATOR).length - 1] + " | grep DualBB").isEmpty()) {
								typeOfFileStrings = new String[] { "CellTrace_DUL1_1", "CellTrace_DUL1_3",
										"CellTrace_DUL3_1", "CellTrace_DUL3_3" };
							}
						} else if (simType.contains(DataAndStringConstants.RNC)) {
							if (!cliCmdHelper.simpleExec("cat " + DataAndStringConstants.SIM_INFO_FILE + " | grep "
									+ sim.split(DataAndStringConstants.SEPARATOR)[sim.split(DataAndStringConstants.SEPARATOR).length - 1] + " | grep DualMultiRAT").isEmpty()) {
								typeOfFileStrings = new String[] { "CellTrace_DUL1_1", "CellTrace_DUL1_3",
										"CellTrace_DUL3_1", "CellTrace_DUL3_3" };
							}
						}

						for (int i = 0; i < typeOfFileStrings.length; i++) {
							String fileWithPath = cliCmdHelper.simpleExec("find " + dirPath + " -type l -name \"*"
									+ typeOfFileStrings[i] + "*\" | sort | head -1").trim();
							if (fileWithPath.isEmpty()) {
								GenericMethodUtils.printMessage(
										" The " + typeOfFileStrings + " output file is not getting generated for node "
												+ node + " of simulation : " + sim,
										DataAndStringConstants.ERROR);
								return 1;
							}
							String actualFilePath = fileWithPath
									.replace(fileWithPath.split(DataAndStringConstants.FRWD_SLASH)[fileWithPath
											.split(DataAndStringConstants.FRWD_SLASH).length - 1], "");
							String latestPmFile = cliCmdHelper.simpleExec("ls -lrt " + actualFilePath + " | grep "
									+ typeOfFileStrings[i] + " | grep -v ^d | tail -1 ").trim().split("\\s+")[8];
							exitCodes.add(compareFileInfo(testcase_Id, sim, node, actualFilePath, expectedFilePath,
									latestPmFile, expectedOutput));
						}
					}
				}
			} else {
				GenericMethodUtils.printMessage(
						"The " + testcase_Id + " is being skipped for " + sim + " as the simulation is not started.",
						DataAndStringConstants.INFO);
			}
		}
		for (int i = 0; i < exitCodes.size(); i++) {
			if (exitCodes.get(i) == 1) {
				GenericMethodUtils.printMessage(
						"File has either not been created, or tests have failed. Check console output for more info.",
						DataAndStringConstants.INFO);
				exitCodes.clear();
				return 1;
			}
		}
		GenericMethodUtils.printMessage("File has been successfully tested.", DataAndStringConstants.INFO);
		exitCodes.clear();
		return 0;
	}

	public String[] getSimList(String sim_type, String node_type, String behaviour) {
		String[] listOfSims = new String[] {};
		if (behaviour.equalsIgnoreCase(DataAndStringConstants.GENSTATS)) {
			String[] listOfEntries = cliCmdHelper.simpleExec(
					"cat " + DataAndStringConstants.SIM_DATA_FILE + " | grep -w " + sim_type + " | grep -w " + node_type)
					.trim().split(DataAndStringConstants.ENTER_CHAR);
			if (cliCmdHelper.simpleExec(
					"cat " + DataAndStringConstants.SIM_DATA_FILE + " | grep -w " + sim_type + " | grep -w " + node_type)
					.trim().isEmpty()) {
				GenericMethodUtils.printMessage("No simulation is present for " + sim_type + DataAndStringConstants.SEPARATOR + node_type + " node.",
						DataAndStringConstants.WARN);
				return listOfSims;
			}
                     if (listOfEntries.length > 0) {
			    listOfSims = new String[listOfEntries.length];
			    for (int i = 0; i < listOfEntries.length; i++) {
				  listOfSims[i] = listOfEntries[i].split("\\s+")[1];
			    }
                     }
		} else if (behaviour.equalsIgnoreCase(DataAndStringConstants.PLAYBACK)) {
			String allSims = cliCmdHelper
					.simpleExec("ls " + DataAndStringConstants.NETSIM_DBDIR_PATH + " | grep " + node_type);
			if (allSims.isEmpty()) {
				GenericMethodUtils.printMessage("No simulation is present for " + sim_type + DataAndStringConstants.SEPARATOR + node_type + " node.",
						DataAndStringConstants.WARN);
				return listOfSims;
			}
			listOfSims = allSims.split(DataAndStringConstants.ENTER_CHAR);
		}

		return listOfSims;
	}

	public String getFinalLoc(String sim, String simType, String nodeType, String subscription, String behaviour) {
		String CfgEntry = "";
		nodeType = nodeType.replace(DataAndStringConstants.SEPARATOR, DataAndStringConstants.UNDERSCORE);
		if ((nodeType.equals(DataAndStringConstants.PRBS)) && (simType.contains(DataAndStringConstants.LTE))) {
			nodeType = DataAndStringConstants.MSRBS_V1;
		}

		if (behaviour.equalsIgnoreCase(DataAndStringConstants.GENSTATS) || cliCmdHelper.simpleExec(
				"cat " + DataAndStringConstants.GENSTATS_CFG + " | grep PLAYBACK_SIM_LIST | grep " + sim) == null) {
			if (subscription.equalsIgnoreCase(DataAndStringConstants.STATS)) {
				CfgEntry = cliCmdHelper.simpleExec(
						"cat " + DataAndStringConstants.GENSTATS_CFG + " | grep " + nodeType + "_PM_FileLocation")
						.trim();

			} else if (subscription.equalsIgnoreCase(DataAndStringConstants.EVENTS)) {
				CfgEntry = cliCmdHelper.simpleExec(
						"cat " + DataAndStringConstants.GENSTATS_CFG + " | grep " + nodeType + "_PMEvent_FileLocation")
						.trim();
			} else {
				GenericMethodUtils.printMessage("Please enter the valid Subscription value in csv file.",
						DataAndStringConstants.ERROR);
			}
		} else if (behaviour.equalsIgnoreCase(DataAndStringConstants.PLAYBACK)) {
			CfgEntry = cliCmdHelper
					.simpleExec(
							"cat " + DataAndStringConstants.GENSTATS_CFG + " | grep " + nodeType + "_PM_FileLocation")
					.trim();
			if (CfgEntry == null || CfgEntry.isEmpty()) {
				CfgEntry = cliCmdHelper.simpleExec(
						"cat " + DataAndStringConstants.PLAYBACK_CFG + " | grep " + nodeType + "_STATS_APPEND_PATH")
						.trim();
			}
		}
		GenericMethodUtils.printMessage("File path in cfg file : " + CfgEntry, DataAndStringConstants.INFO);

		if (CfgEntry == null || CfgEntry.isEmpty()) {
			// Returns default path
			return (DataAndStringConstants.FS_DEFAULT_FILE_PATH);
		} else {
			CfgEntry = CfgEntry.split(DataAndStringConstants.EQUALS)[1].trim().replace("\"", "");
			if (!CfgEntry.endsWith(DataAndStringConstants.FRWD_SLASH)) {
				CfgEntry = CfgEntry.concat(DataAndStringConstants.FRWD_SLASH);
			}
			if (CfgEntry.contains(DataAndStringConstants.FS_PATH)) {
				return CfgEntry;
			} else {
				return DataAndStringConstants.FS_PATH + CfgEntry;
			}
		}
	}

	public Integer compareFileInfo(String testcaseName, String simulation, String node, String actualFilePath,
			String expectedFilePath, String latestPmFile, String expectedOutput) {
		if (testcaseName.contains(DataAndStringConstants.EXTENSION)) {
			expectedOutput.trim();
			String actualExtension = cliCmdHelper
					.simpleExec("ls " + actualFilePath + latestPmFile + " | rev | cut -d '.' -f1 | rev ").trim();
			if (actualExtension.equalsIgnoreCase(expectedOutput)) {
				GenericMethodUtils
						.printMessage(
								"Actual extension: " + actualExtension + " Expected extension: " + expectedOutput
										+ " .Extension is correctly assigned to " + latestPmFile,
								DataAndStringConstants.INFO);
				return 0;
			} else {
				GenericMethodUtils.printMessage(
						"Actual extension: " + actualExtension + " Expected extension: " + expectedOutput
								+ " .Extension is NOT correctly assigned to " + latestPmFile,
						DataAndStringConstants.ERROR);
				return 1;
			}
		} else if (testcaseName.contains(DataAndStringConstants.SIZE)) {
			int minExpectedSize = Integer.parseInt(expectedOutput.split(DataAndStringConstants.SEPARATOR)[0]);
			int maxExpectedSize = Integer.parseInt(expectedOutput.split(DataAndStringConstants.SEPARATOR)[1]);
			String actualFileSize = cliCmdHelper.simpleExec("stat -Lc %s " + actualFilePath + latestPmFile).trim();
			if (Integer.parseInt(actualFileSize) >= minExpectedSize
					&& Integer.parseInt(actualFileSize) <= maxExpectedSize) {
				GenericMethodUtils.printMessage(
						"File Size of " + latestPmFile + " is : " + actualFileSize + " .File size is correct",
						DataAndStringConstants.INFO);
				return 0;
			} else {
				GenericMethodUtils.printMessage(
						"File Size of " + latestPmFile + " is : " + actualFileSize + " .File size is NOT correct",
						DataAndStringConstants.ERROR);
				return 1;
			}
		} else if (testcaseName.contains(DataAndStringConstants.PATH)) {
			String outputCode = DataAndStringConstants.ONE;
			if (actualFilePath.equals(expectedFilePath)) {
				outputCode = DataAndStringConstants.ZERO;
			}
			if (outputCode.equalsIgnoreCase(expectedOutput)) {
				GenericMethodUtils.printMessage(
						"Output file path is correct for node " + node + " of simulation " + simulation,
						DataAndStringConstants.INFO);
				return 0;
			} else {
				GenericMethodUtils.printMessage("File is NOT generating at correct path for simulation " + simulation,
						DataAndStringConstants.ERROR);
				return 1;
			}
		}
		return 0;
	}
}
