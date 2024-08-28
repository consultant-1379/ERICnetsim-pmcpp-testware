/*------------------------------------------------------------------------------
 *******************************************************************************
 * COPYRIGHT Ericsson 2018
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
import com.ericsson.cifwk.netsim.GenericTestsOperator;
import com.ericsson.cifwk.netsim.GenericTestsOperatorInterface;

import com.ericsson.cifwk.taf.TestCase;
import com.ericsson.cifwk.taf.TorTestCaseHelper;
import com.ericsson.cifwk.taf.annotations.Context;
import com.ericsson.cifwk.taf.annotations.DataDriven;
import com.ericsson.cifwk.taf.annotations.Input;
import com.ericsson.cifwk.taf.annotations.Output;
import com.ericsson.cifwk.taf.annotations.TestId;
import com.ericsson.cifwk.taf.guice.OperatorRegistry;

import utils.GenericMethodUtils;

/**
 * Executes scripts and verify expected output
 */
public class GenericTests extends TorTestCaseHelper implements TestCase 
{

	private static final String INFO = "INFO", WARN = "WARN", ERROR = "ERROR";
	@Inject
	OperatorRegistry<GenericTestsOperator> operatorRegistry;
	
	@BeforeSuite
	public void initialise() {
		assertTrue(new GenericTestsOperator().initialise());
	}

	@TestId(id = "genstatsreport", title = "Generic Test")
	@Test(groups = { "Acceptance" })
	@DataDriven(name = "GenericTests")
	@Context(context = { Context.CLI })
	public void runGenericTest(@Input("testCase_Id") final String testCase_Id,@Input("simType") final String simType,@Input("nodeType") final String nodeType,@Input("subscription") final String subscription,@Input("behaviour") final String behaviour,@Output("expectedOutput") final String expectedOutput) 
	{
			final GenericTestsOperatorInterface seOperator = operatorRegistry.provide(GenericTestsOperator.class);
			final int scriptExecutionExitCode = seOperator.verifyGenericTestScriptExecution(testCase_Id,simType,nodeType,subscription,behaviour,expectedOutput);
			final boolean testCondition = scriptExecutionExitCode == 0;
			if (!testCondition) 
			{
				throw new TestCaseException("Returned exit code: " + scriptExecutionExitCode + ", Hence the test case " + testCase_Id + " failed for node " + nodeType );
			}
			assertTrue(testCondition);
		}
	}
