package com.ericsson.cifwk.netsim.test.cases;

import javax.inject.Inject;

import org.testng.annotations.BeforeSuite;
import org.testng.annotations.Test;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.ericsson.cifwk.netsim.HealthCheckOperator;
import com.ericsson.cifwk.netsim.UnitTestOperatorInterface;
import com.ericsson.cifwk.taf.TestCase;
import com.ericsson.cifwk.taf.TorTestCaseHelper;
import com.ericsson.cifwk.taf.annotations.*;
import com.ericsson.cifwk.taf.guice.OperatorRegistry;

/**
 * Executes scripts and verify expected output
 */
public class HealthCheckTest extends TorTestCaseHelper implements TestCase {

    private static final Logger logger = LoggerFactory.getLogger(HealthCheckTest.class);
	
    @Inject
    OperatorRegistry<HealthCheckOperator> operatorRegistry;

    @BeforeSuite
	public void initialise() {
        assertTrue(new HealthCheckOperator().initialise());
    }

    /**
     * Executes scripts on a remote server which defined in host.properties file.
     *
     * @DESCRIPTION Verify the script executions
     * @PRE Copy the scripts to remote server be tested
     * @VUsers 1
     * @PRIORITY HIGH Note: NETSUP-2838 Check html report for full explanation behind failures
     */
    @TestId(id = "genstatsreport", title = "Verify the genstats health check script executions")
    @Test(groups = { "Acceptance" })
    @DataDriven(name = "HealthCheckTest")
    @Context(context = { Context.CLI })
    public void verifyGenstatHealthCheck(@Input("command") final String command, @Output("expectedExitCode") final int expectedExitCode) {
    	 final UnitTestOperatorInterface seOperator = operatorRegistry.provide(HealthCheckOperator.class);
        final int scriptExecutionExitCode = seOperator.verifyScriptExecution(command);
        final boolean testCondition = scriptExecutionExitCode == expectedExitCode;
        System.out.println("Expected exit code: "+ expectedExitCode + " script exit code : " + scriptExecutionExitCode );
        if (!testCondition) {
            throw new TestCaseException("Returned exit code: " + scriptExecutionExitCode + ",  while expecting exit code: " + expectedExitCode);
        }
        assertTrue(testCondition);
    }
}