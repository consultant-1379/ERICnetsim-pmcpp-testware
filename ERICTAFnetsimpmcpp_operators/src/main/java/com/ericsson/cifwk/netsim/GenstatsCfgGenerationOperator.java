package com.ericsson.cifwk.netsim;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import utils.HostHandler;

import com.ericsson.cifwk.taf.annotations.Context;
import com.ericsson.cifwk.taf.annotations.Operator;
import com.ericsson.cifwk.taf.tools.cli.CLICommandHelper;
import com.ericsson.cifwk.taf.data.DataHandler;

@Operator(context = Context.CLI)
public class GenstatsCfgGenerationOperator implements UnitTestOperatorInterface {

	/** Taf command handler instance */
	private static CLICommandHelper cliCmdHelper;

	/** Logging utility */
	private static final Logger logger = LoggerFactory.getLogger(GenstatsCfgGenerationOperator.class);

	public boolean initialise() {
		try {
			cliCmdHelper = new CLICommandHelper(HostHandler.getTargetHost());
			return true;
		} catch (final Exception e) {
			System.out.println("[ERROR]: Error occured while initialising the TAF env.");
			return false;
		}
	}

	/**
	 * Method for running commands given by the commands .csv file linked via
	 * datadriven.properties file.
	 **/
	public int verifyScriptExecution(String command) {
		logger.info("Verifying the process of cfg generation execution.");
		// Fetching variable from jenkins job
		String nssDrop = DataHandler.getAttribute("nssDrop").toString().trim();
		String deplType = DataHandler.getAttribute("DEPLOYMENT_TYPE").toString();
		String counterVolume = DataHandler.getAttribute("REQUIRED_COUNTER_VOLUME").toString();
		String cfgCommandArgs = " --nssRelease " + nssDrop + " --deplType " + deplType + " --counterVolume "+ counterVolume;
              System.out.println("Verifying the process of cfg generation execution.");
		if (command.contains("cfgGenerator")) {
			System.out.println("Command to be executed :"+ command + cfgCommandArgs);
			cliCmdHelper.execute(command + cfgCommandArgs);
			return cliCmdHelper.getCommandExitValue();
		} else if (command.contains(".sh")) {
			cliCmdHelper.execute(command);
			return cliCmdHelper.getCommandExitValue();
		} else if (command.contains(".py")) {
			cliCmdHelper.execute("python " + command);
			return cliCmdHelper.getCommandExitValue();
		} else {
			//Failure
			return 1;
		}

	}

	@Override
	public int verifyUnitTestScriptExecution(String id, String command) {
		// TODO Auto-generated method stub
		return 0;
	}
}