package com.ericsson.cifwk.netsim.test.cases;

import javax.inject.Inject;

import org.testng.annotations.BeforeSuite;
import org.testng.annotations.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.ericsson.cifwk.netsim.GetSimulationDataOperator;
import com.ericsson.cifwk.netsim.UnitTestOperatorInterface;
import com.ericsson.cifwk.netsim.GetEUtranDataOperator;
import com.ericsson.cifwk.taf.TestCase;
import com.ericsson.cifwk.taf.TorTestCaseHelper;
import com.ericsson.cifwk.taf.annotations.*;
import com.ericsson.cifwk.taf.guice.OperatorRegistry;

/**
 * Executes scripts and verify expected output
 */
public class GetEUtranDataTest extends TorTestCaseHelper implements TestCase {

private static final Logger logger = LoggerFactory.getLogger(GetEUtranDataTest.class);
	
    @Inject
    OperatorRegistry<GetEUtranDataOperator> operatorRegistry;

    @BeforeSuite
    public void initialise() {
        assertTrue(new GetEUtranDataOperator().initialise());
    }

    /**
     * Executes scripts on a remote server which defined in host.properties file.
     *
     * @DESCRIPTION Verify the script executions
     * @PRE Copy the scripts to remote server be tested
     * @VUsers 1
     * @PRIORITY HIGH Note: NETSUP-2838 Check html report for full explanation behind failures
     */
    @TestId(id = "GetEUtranDataTest", title = "Verify EUtran steps of GenStats")
    @Test(groups = { "Acceptance" })
    @DataDriven(name = "GetEUtranDataTest")
    @Context(context = { Context.CLI })
    public void verifyPreInstallation(@Input("command") final String command, @Output("expectedExitCode") final int expectedExitCode) {
		final UnitTestOperatorInterface seOperator = operatorRegistry.provide(GetEUtranDataOperator.class);
        final int scriptExecutionExitCode = seOperator.verifyScriptExecution(command);
        final boolean testCondition = scriptExecutionExitCode == expectedExitCode;
        if (!testCondition) {
            throw new TestCaseException("Returned exit code: " + scriptExecutionExitCode + ",  while expecting exit code: " + expectedExitCode);
        }
        assertTrue(testCondition);
    }
}