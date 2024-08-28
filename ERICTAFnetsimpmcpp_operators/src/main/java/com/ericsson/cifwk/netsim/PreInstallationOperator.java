package com.ericsson.cifwk.netsim;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import utils.HostHandler;

import com.ericsson.cifwk.taf.annotations.Operator;
import com.ericsson.cifwk.taf.data.Host;
import com.ericsson.cifwk.taf.data.User;
import com.ericsson.cifwk.taf.data.UserType;
import com.ericsson.cifwk.taf.tools.cli.CLICommandHelper;
import com.ericsson.cifwk.taf.data.DataHandler;
import com.ericsson.cifwk.taf.annotations.Context;

@Operator(context = Context.CLI)
public class PreInstallationOperator implements UnitTestOperatorInterface {

	/** Taf command handler instance */
	private static CLICommandHelper cliCmdHelper;
	private static CLICommandHelper cliRootCmdHelper;

	private static PreInstallationOperator pioObj;
	private static String RPM_PACKAGE = "ERICnetsimpmcpp_CXP9029065.rpm";

	/** Logging utility */
	private static final Logger logger = LoggerFactory
			.getLogger(PreInstallationOperator.class);

	public boolean initialise() {
		try {
			cliCmdHelper = new CLICommandHelper(HostHandler.getTargetHost());
			cliRootCmdHelper = new CLICommandHelper(
					HostHandler.getTargetHost(), new User("root", "shroot",
							UserType.ADMIN));
			pioObj = new PreInstallationOperator();
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
		System.out.println("Verifying the process of pre installation execution");
		String rpmVersion = "", nssDrop = "", recordingFileVersion = "", deplType = "", isEdeStats = "";
		try {
			rpmVersion = DataHandler.getAttribute("RPM_VERSION").toString().trim();
			nssDrop = DataHandler.getAttribute("nssDrop").toString().trim();
			recordingFileVersion = DataHandler.getAttribute("RECORDING_FILES_OVERRIDE").toString();
			deplType = DataHandler.getAttribute("DEPLOYMENT_TYPE").toString();
			isEdeStats = DataHandler.getAttribute("DEPLOY_EDESTATS").toString();

		} catch (Exception e) {
		}

		System.out.println("TAF Parameter : RPM Version--> " + rpmVersion
				+ " rpmVersion--> " + rpmVersion + " nssDrop--> " + nssDrop
				+ " recordingFileVersion--> " + recordingFileVersion
				+ " deplType--> " + deplType + " isEdeStats--> " + isEdeStats);

		if (null != rpmVersion && !rpmVersion.isEmpty()) {
			command = command + " -r " + rpmVersion;
		}

		if (null != nssDrop && !nssDrop.isEmpty()) {
			command = command + " -n " + nssDrop;
		}

		if (null != recordingFileVersion && !recordingFileVersion.isEmpty()) {
			command = command + " -c " + recordingFileVersion;
		}

		if (null != deplType && !deplType.isEmpty()) {
			command = command + " -d " + deplType;
		}

		if (null != isEdeStats && !isEdeStats.isEmpty()) {
			command = command + " -e " + isEdeStats;
		}
		// Create object to execute commands with root user
		// User username = new User();
		// username.setUsername("root");
		// username.setPassword("shroot");
		// CLICommandHelper cch = new CLICommandHelper();
		// cch.createCliInstance(HostHandler.getTargetHost(), username);

		// Step 1: Download GenStats RPM
		System.out.println("[INFO]: Starting RPM installation.");
		// return pioObj.downloadRPM(cch, rpmVersion);
		if (downloadRPM(cliRootCmdHelper, rpmVersion) == 0) {
			System.out.println("[INFO]: RPM with version " + rpmVersion
					+ " has been downloaded sucessfully.");
		} else {
			System.out.println("[WARN]: RPM Downloading failed.");
		}

		if (installRPM(cliRootCmdHelper) == 0) {
			System.out.println("[INFO]: RPM has been installed sucessfully.");
		} else {
			System.out.println("[INFO]: RPM installation failed.");
		}

		System.out.println("[INFO]: Command to be excuted: " + command);
		// Step 2: Execute pre-installation of genstats
		if (command.contains("pre_execution")) {
			cliCmdHelper.execute(command);
			return cliCmdHelper.getCommandExitValue();
		} else if (command.contains(".sh")) {
			cliCmdHelper.execute(command);
			return cliCmdHelper.getCommandExitValue();
		} else if (command.contains(".py")) {
			cliCmdHelper.execute("python " + command);
			return cliCmdHelper.getCommandExitValue();
		} else {
			// Failure
			return 1;
		}

	}

	private static int downloadRPM(CLICommandHelper cch, String rpm_version) {
		if (rpm_version.contains("SNAPSHOT")) {
			cch.execute("curl -L \"https://arm1s11-eiffel004.eiffel.gic.ericsson.se:8443/nexus/service/local/artifact/maven/redirect?r=snapshots&g=com.ericsson.cifwk.netsim&a=ERICnetsimpmcpp_CXP9029065&p=rpm&v="
					+ rpm_version + "\" -o /tmp/ERICnetsimpmcpp_CXP9029065.rpm");
		} else {
			cch.execute("curl  -L \"https://arm1s11-eiffel004.eiffel.gic.ericsson.se:8443/nexus/service/local/artifact/maven/redirect?r=releases&g=com.ericsson.cifwk.netsim&a=ERICnetsimpmcpp_CXP9029065&p=rpm&v="
					+ rpm_version + "\" -o /tmp/ERICnetsimpmcpp_CXP9029065.rpm");
		}
		return cch.getCommandExitValue();
	}

	private static int installRPM(CLICommandHelper cch) {
              cch.execute("rm -rf /netsim_users/*");
		cch.execute("rpm -Uvh --force /tmp/" + RPM_PACKAGE);
		cch.execute("chown netsim:netsim /netsim_users/ -R");
		cch.execute("rm /tmp/" + RPM_PACKAGE);
		cch.execute("chown -R netsim:netsim /pms_tmpfs/");
		return cch.getCommandExitValue();
	}

	@Override
	public int verifyUnitTestScriptExecution(String id, String command) {
		// TODO Auto-generated method stub
		return 0;
	}
}
