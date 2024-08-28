/**
 * -----------------------------------------------------------------------
 *     Copyright (C) 2016 LM Ericsson Limited.  All rights reserved.
 * -----------------------------------------------------------------------
 */
package utils;

import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.ericsson.cifwk.taf.data.DataHandler;
import com.ericsson.cifwk.taf.data.Host;
import com.ericsson.nms.host.HostConfigurator;

/**
 * Handles different type hosts to be captured.
 * 
 * @author qfatonu
 * 
 */
public class HostHandler {

	/** Logging utility */
	private static final Logger logger = LoggerFactory
			.getLogger(HostHandler.class);

	private static final String VAPP_MASTER_SERVER_IP = "192.168.0.42";

	/** List of the hosts connected to DMT */
	private static List<Host> hosts = HostConfigurator.getAllNetsimHosts();

	/**
	 * Returns the correspondence available host by checking jenkins and
	 * properties args.
	 * 
	 * @return available host by in order of MV job, cluster-id and
	 *         physical-or-vm-netsim
	 */
	public static Host getTargetHost() {

		String serverName = null;
		try {
			serverName = DataHandler.getAttribute("serverName").toString()
					.replace("\"", "");
		} catch (final NullPointerException e) {
			System.out.println("HostSetup::noServerNames");
		}

		if (serverName != null && !serverName.isEmpty()) {
			final Host host = DataHandler.getHostByName(serverName);
			System.out.println("HostSetup::serverName= {} ==" + host);
			if (null != host) {
				return host;
			}
		}

		for (final Host host : HostConfigurator.getAllNetsimHosts()) {
			System.out.println("DMT-host:{} == " + host.getHostname()
					+ "Server Name = {} ==" + serverName);
			if (host.getHostname().equals(serverName)) {
				return host;
			}
		}

		if (HostConfigurator.getNetsim() != null) {
			final Host host = HostConfigurator.getNetsim();
			System.out.println("HostSetup::hostConfigurator={} == "
					+ host.toString());
			return host;
		}

		final Host host = DataHandler.getHostByName("physical-or-vm-netsim");
		logger.debug("HostSetup::LocalProperties= {}", host.toString());

		return host;

	}

	public static String getMasterServerIp() {
		if (HostConfigurator.getNetsim() != null) {
			final Host host = HostConfigurator.getMS();
			logger.debug("getMasterServerIp::HostSetup::hostConfigurator={}",
					host.toString());
			return host.getIp();
		} else {
			logger.debug("getMasterServerIp::HostSetup::staticVappMSIP={}",
					VAPP_MASTER_SERVER_IP);
			return VAPP_MASTER_SERVER_IP;
		}
	}
}