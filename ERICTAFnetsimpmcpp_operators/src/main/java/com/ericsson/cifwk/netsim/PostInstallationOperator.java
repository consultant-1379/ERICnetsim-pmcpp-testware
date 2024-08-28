package com.ericsson.cifwk.netsim;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import utils.HostHandler;

import com.ericsson.cifwk.taf.annotations.Context;
import com.ericsson.cifwk.taf.annotations.Operator;
import com.ericsson.cifwk.taf.tools.cli.CLICommandHelper;
import com.ericsson.cifwk.taf.data.DataHandler;

@Operator(context = Context.CLI)
public class PostInstallationOperator implements UnitTestOperatorInterface {

	/** Taf command handler instance */
	private static CLICommandHelper cliCmdHelper;
	private static String hostname;

	/** Logging utility */
	private static final Logger logger = LoggerFactory.getLogger(PostInstallationOperator.class);

	public boolean initialise() {
		try {
			cliCmdHelper = new CLICommandHelper(HostHandler.getTargetHost());
			hostname = HostHandler.getTargetHost().getHostname();
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
	@Override
	public int verifyScriptExecution(String command) {
		logger.info("Verifying the process of post installation executions on " + hostname);
		String ropDuration = "", deplType = "";
		try {
			ropDuration = DataHandler.getAttribute("GPEH_PM_ROP_DURATION").toString().trim();
                        deplType = DataHandler.getAttribute("DEPLOYMENT_TYPE").toString().trim();

		} catch (Exception e) {
		}
		
		if (null != ropDuration && !ropDuration.isEmpty() && command.contains("gpehRopConfig")) {
			if(ropDuration.trim().equals("1 min")){
				command = command + " 1";
			}else if (ropDuration.trim().equals("15 min")){
				command = command + " 15";
			}
			
		}
		
	        if (command.contains("post_execution")){
        	      cliCmdHelper.execute(command+" -c /tmp/"+hostname);
    		      return cliCmdHelper.getCommandExitValue();
                }else if (command.contains("gpehRopConfig")) {
        	      if(null != deplType && !deplType.isEmpty() && !deplType.equalsIgnoreCase("NSS")){
                           cliCmdHelper.execute("python " + command);
                           return cliCmdHelper.getCommandExitValue();
        	       }else {
        		   return 0;
        	       }
 	    }else if (command.contains(".sh")) {
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
