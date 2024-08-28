package com.ericsson.cifwk.netsim;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import utils.GenericMethodUtils;
import utils.HostHandler;

import com.ericsson.cifwk.taf.annotations.Context;
import com.ericsson.cifwk.taf.annotations.Operator;
import com.ericsson.cifwk.taf.data.User;
import com.ericsson.cifwk.taf.data.UserType;
import com.ericsson.cifwk.taf.tools.cli.CLICommandHelper;

@Operator(context = Context.CLI)
public class UnitTestOperator implements UnitTestOperatorInterface {

	/** Taf command handler instance */
	private static CLICommandHelper cliCmdHelper;
	private static CLICommandHelper cliRootCmdHelper;
	private static final String HOSTNAME = "hostname";
	private static final String GENSTATS_CFG = "/netsim/netsim_cfg";
	private static final String INFO = "INFO", WARN = "WARN", ERROR = "ERROR";
	private static String cliCommand = null;

	/** Logging utility */
	private static final Logger logger = LoggerFactory.getLogger(PreInstallationOperator.class);

	public boolean initialise() {
		try {
			cliCmdHelper = new CLICommandHelper(HostHandler.getTargetHost());
			cliRootCmdHelper = new CLICommandHelper(HostHandler.getTargetHost(), new User("root", "shroot",UserType.ADMIN));
			return true;
		} catch (final Exception e) {
			GenericMethodUtils.printMessage("Error occured while initialising the TAF env.", ERROR);
			return false;
		}
	}

	/**
	 * Method for running commands given by the commands .csv file linked via
	 * datadriven.properties file.
	 **/
	public int verifyUnitTestScriptExecution(String test_id, String csvCommand) {
		logger.info("Verifying the process of unit test execution");
		GenericMethodUtils.printMessage("Executing unit testcases for Genstats.", INFO);
		Map<String, String> nodeBwMap = new HashMap<>();
		String[] nodeTypes = { "TCU02:128000bit", "SIU02:128000bit" };

		if (GenericMethodUtils.isFileExists(GENSTATS_CFG, cliRootCmdHelper).equalsIgnoreCase("FALSE")) {
			GenericMethodUtils.printMessage(GENSTATS_CFG + " file not present.", ERROR);
			return 1;
		}

		String[] simList = GenericMethodUtils.getCfgSimList(HOSTNAME,GENSTATS_CFG, cliRootCmdHelper);
		if (simList.length < 1) {
			GenericMethodUtils.printMessage("Simulation list is empty in " + GENSTATS_CFG, WARN);
			return 1;
		}

		GenericMethodUtils.printMessage("Getting bandwidth data.", INFO);
		cliCommand = csvCommand + " -n -s | awk -F' ' '{print $1\":\"$2}' | sed -n '1!p'";
		String[] nodeBwArray = cliRootCmdHelper.simpleExec(cliCommand).split("\r\n");
		if (nodeBwArray.length < 1) {
			GenericMethodUtils.printMessage("Bandwidth haven't set on server " + HOSTNAME, WARN);
			return 1;
		}

		for (String nodeBw : nodeBwArray) {
			String[] temp = nodeBw.split(":");
			nodeBwMap.put(temp[0], temp[1]);
		}
		GenericMethodUtils.printMessage("Loading of Bandwith map completed.",INFO);

		Set<String> failureSims = new HashSet<>();

		for (String sim : simList) {
			String[] nodeList = null;
			String expectedBWValue = null;
			for (String type : nodeTypes) {
				if (sim.contains(type.split(":")[0])) {
					GenericMethodUtils.printMessage("Processing sim : " + sim,INFO);
					expectedBWValue = type.split(":")[1];
					nodeList = GenericMethodUtils.removeNewLineCharacter(cliCmdHelper.simpleExec("echo $(ls /netsim/netsim_dbdir/simdir/netsim/netsimdir/" + sim + ")").trim()).split(" ");
					if (nodeList.length > 0) {
						for (String node : nodeList) {
							if (!nodeBwMap.containsKey(node) || null == nodeBwMap.get(node) || nodeBwMap.get(node).equals("") || !nodeBwMap.get(node).equals(expectedBWValue)) {
								if (null == nodeBwMap.get(node) || !nodeBwMap.containsKey(node)) {
									GenericMethodUtils.printMessage("Failed due to bandwidth not allocated for node : " + node + " , Expected Bandwidth : " + expectedBWValue, ERROR);
								} else {
									GenericMethodUtils.printMessage("Failed due to bandwidth mismatch for node : " + node + " , Expected Bandwidth : " + expectedBWValue + " , Actual Bandwidth : " + nodeBwMap.get(node),ERROR);
								}
								failureSims.add(sim);
							}
						}
					} else {
						failureSims.add(sim);
					}
					break;
				}
			}
		}
		if (failureSims.size() > 0) {
			GenericMethodUtils.printMessage("Issue found related to bandwidth for sim(s) : " + failureSims, ERROR);
			return 1;
		}
		return 0;
	}

	@Override
	public int verifyScriptExecution(String command) {
		// TODO Auto-generated method stub
		return 0;
	}
}
