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
package com.ericsson.cifwk.netsim.test.cases;

import javax.inject.Inject;

import org.testng.annotations.BeforeSuite;
import org.testng.annotations.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.ericsson.cifwk.netsim.GetEUtranDataOperator;
import com.ericsson.cifwk.netsim.UnitTestOperatorInterface;
import com.ericsson.cifwk.netsim.LimitBandwidthOperator;
import com.ericsson.cifwk.taf.TestCase;
import com.ericsson.cifwk.taf.TorTestCaseHelper;
import com.ericsson.cifwk.taf.annotations.*;
import com.ericsson.cifwk.taf.guice.OperatorRegistry;

public class LimitBandwidthTest extends TorTestCaseHelper implements TestCase {

    private static final Logger logger = LoggerFactory.getLogger(LimitBandwidthTest.class);
	
    @Inject
    OperatorRegistry<LimitBandwidthOperator> operatorRegistry;

    @BeforeSuite
    public void init() {
        assertTrue(new LimitBandwidthOperator().initialise());
    }


    @TestId(id = "LimitBandwidthTest", title = "Verify the Limit Bandwidth executions")
    @Test(groups = { "Acceptance" })
    @DataDriven(name = "LimitBandwidthTest")
    @Context(context = { Context.CLI })
    public void verifyScriptExecution(@Input("commands") final String command, @Output("expectedExitCode") final int expectedExitCode){
          final UnitTestOperatorInterface seOperator = operatorRegistry.provide(LimitBandwidthOperator.class);
          final int scriptExecutionExitCode = seOperator.verifyScriptExecution(command);
          final boolean testCondition = scriptExecutionExitCode == expectedExitCode;
          if (!testCondition) {
             throw new TestCaseException("Returned exit code: " + scriptExecutionExitCode + ",  while expecting exit code: " + expectedExitCode);
          }
          assertTrue(testCondition);
    }
}