package com.ericsson.cifwk.netsim.test.cases;

import javax.inject.Inject;

import org.testng.annotations.BeforeSuite;
import org.testng.annotations.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.ericsson.cifwk.netsim.GetEUtranDataOperator;
import com.ericsson.cifwk.netsim.UnitTestOperatorInterface;
import com.ericsson.cifwk.netsim.TemplateGeneratorOperator;
import com.ericsson.cifwk.taf.TestCase;
import com.ericsson.cifwk.taf.TorTestCaseHelper;
import com.ericsson.cifwk.taf.annotations.*;
import com.ericsson.cifwk.taf.guice.OperatorRegistry;

/**
 * Executes scripts and verify expected output
 */
public class TemplateGeneratorTest extends TorTestCaseHelper implements TestCase {

private static final Logger logger = LoggerFactory.getLogger(TemplateGeneratorTest.class);
	
    @Inject
    OperatorRegistry<TemplateGeneratorOperator> operatorRegistry;

    @BeforeSuite
    public void init() {
        assertTrue(new TemplateGeneratorOperator().initialise());
    }

    /**
     * Executes scripts on a remote server which defined in host.properties file.
     *
     * @DESCRIPTION Verify the script executions
     * @PRE Copy the scripts to remote server be tested
     * @VUsers 1
     * @PRIORITY HIGH Note: NETSUP-2838 Check html report for full explanation behind failures
     */
    @TestId(id = "TemplateGeneratorTest", title = "Verify Template Generator executions of GenStats")
    @Test(groups = { "Acceptance" })
    @DataDriven(name = "TemplateGeneratorTest")
    @Context(context = { Context.CLI })
    public void verifyTemplateGenerator(@Input("command") final String command, @Output("expectedExitCode") final int expectedExitCode) {
        final UnitTestOperatorInterface seOperator = operatorRegistry.provide(TemplateGeneratorOperator.class);
        final int scriptExecutionExitCode = seOperator.verifyScriptExecution(command);
        final boolean testCondition = scriptExecutionExitCode == expectedExitCode;
        if (!testCondition) {
            throw new TestCaseException("Returned exit code: " + scriptExecutionExitCode + ",  while expecting exit code: " + expectedExitCode);
        }
        assertTrue(testCondition);
    }
}