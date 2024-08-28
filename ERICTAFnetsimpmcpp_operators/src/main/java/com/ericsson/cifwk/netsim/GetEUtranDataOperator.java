package com.ericsson.cifwk.netsim;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import utils.HostHandler;

import com.ericsson.cifwk.taf.annotations.Context;
import com.ericsson.cifwk.taf.annotations.Operator;
import com.ericsson.cifwk.taf.tools.cli.CLICommandHelper;
import com.ericsson.cifwk.taf.data.DataHandler;

@Operator(context = Context.CLI)
public class GetEUtranDataOperator implements UnitTestOperatorInterface {

	/** Taf command handler instance */
	private static CLICommandHelper cliCmdHelper;

	/** Logging utility */
	private static final Logger logger = LoggerFactory
			.getLogger(GetEUtranDataOperator.class);

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
		System.out.println("[INFO]: Verifying the process of fetching EUtran Cell Data.");
		String deplType = DataHandler.getAttribute("DEPLOYMENT_TYPE").toString();

		if (null != deplType && !deplType.isEmpty()) {
			command = command + " -d " + deplType;
		}

		System.out.println("[INFO]: Command to be executed is : " + command);
              
		if (command.contains("getEutran")) {
                     System.out.println(cliCmdHelper.execute(command));
			if (cliCmdHelper.execute(command).contains("ERROR")) {
				return 1;
			} else {
				return 0;
			}
		} else if (command.contains(".sh")) {
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