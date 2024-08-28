package com.ericsson.cifwk.netsim;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import utils.HostHandler;

import com.ericsson.cifwk.taf.annotations.Context;
import com.ericsson.cifwk.taf.annotations.Operator;
import com.ericsson.cifwk.taf.tools.cli.CLICommandHelper;

@Operator(context = Context.CLI)
public class GetSimulationDataOperator implements UnitTestOperatorInterface {

	/** Taf command handler instance */
	private static CLICommandHelper cliCmdHelper;

	/** Logging utility */
	private static final Logger logger = LoggerFactory
			.getLogger(GetSimulationDataOperator.class);

	public boolean initialise() {
		try {
			cliCmdHelper = new CLICommandHelper(HostHandler.getTargetHost());
			return true;
		} catch (final Exception e) {
			System.out
					.println("[ERROR]: Error occured while initialising the TAF env.");
			return false;
		}
	}

	/**
	 * Method for running commands given by the commands .csv file linked via
	 * datadriven.properties file.
	 **/
	public int verifyScriptExecution(String command) {
		logger.info("Verifying the process of fetching health check execution on ");
		System.out.println("[INFO]: Command to be executed is : " + command);
		if (command.contains(".sh")) {
			cliCmdHelper.execute(command);
			return cliCmdHelper.getCommandExitValue();
		} else if (command.contains(".py")) {
			cliCmdHelper.execute("python " + command);
			return cliCmdHelper.getCommandExitValue();
		} else {
			// failure
			return 1;
		}
	}

	@Override
	public int verifyUnitTestScriptExecution(String id, String command) {
		// TODO Auto-generated method stub
		return 0;
	}
}