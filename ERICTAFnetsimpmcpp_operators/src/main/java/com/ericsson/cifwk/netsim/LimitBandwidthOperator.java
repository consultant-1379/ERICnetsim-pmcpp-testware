/*------------------------------------------------------------------------------
 *******************************************************************************
 * COPYRIGHT Ericsson 2017
 *
 * The copyright to the computer program(s) herein is the property of
 * Ericsson Inc. The programs may be used and/or copied only with written
 * permission from Ericsson Inc. or in accordance with the terms and
 * conditions stipulated in the agreement/contract under which the
 * program(s) have been supplied.
 *******************************************************************************
 *----------------------------------------------------------------------------*/
package com.ericsson.cifwk.netsim;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.ericsson.cifwk.taf.annotations.Context;
import com.ericsson.cifwk.taf.annotations.Operator;
import com.ericsson.cifwk.taf.tools.cli.CLICommandHelper;

import utils.HostHandler;

@Operator(context = Context.CLI)
public class LimitBandwidthOperator implements UnitTestOperatorInterface {

	/** Taf command handler instance */
	private static CLICommandHelper cliCmdHelper;

	/** Logging utility */
	private static final Logger logger = LoggerFactory.getLogger(LimitBandwidthOperator.class);

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

	/*
	 * (non-Javadoc)
	 * 
	 * @see com.ericsson.cifwk.netsim.LimitBandwidthOperatorInterface#
	 * verifyScriptExecution(java.lang.String)
	 */
	public int verifyScriptExecution(String command) {
		logger.info("Verifying the process of limiting bandwidth executions.");
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