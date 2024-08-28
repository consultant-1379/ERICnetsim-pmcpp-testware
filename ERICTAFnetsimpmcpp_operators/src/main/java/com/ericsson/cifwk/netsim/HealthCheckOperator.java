package com.ericsson.cifwk.netsim;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.regex.Pattern;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import utils.*;

import com.ericsson.cifwk.taf.annotations.Context;
import com.ericsson.cifwk.taf.annotations.Operator;
import com.ericsson.cifwk.taf.data.*;
import com.ericsson.cifwk.taf.handlers.RemoteFileHandler;
import com.ericsson.cifwk.taf.handlers.implementation.LocalCommandExecutor;
import com.ericsson.cifwk.taf.tools.cli.CLICommandHelper;

import utils.HostHandler;

@Operator(context = Context.CLI)
public class HealthCheckOperator implements UnitTestOperatorInterface {

    /** Taf command handler instance */
    private static CLICommandHelper cliCmdHelper;

    /** Logging utility */
    private static final Logger logger = LoggerFactory.getLogger(HealthCheckOperator.class);

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
     * Method for running commands given by the commands .csv file linked via datadriven.properties file.
     **/
    public int verifyScriptExecution(String command) {
        logger.info("Verifying the process of fetching health check execution on ");
        System.out.println(cliCmdHelper.execute(command));
        if(cliCmdHelper.execute(command).contains("ERROR")){
            	return 1;
        }else{
            	return 0;
        }
    }

	@Override
	public int verifyUnitTestScriptExecution(String id, String command) {
		// TODO Auto-generated method stub
		return 0;
	}

}