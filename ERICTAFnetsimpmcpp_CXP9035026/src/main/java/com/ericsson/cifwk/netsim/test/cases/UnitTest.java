package com.ericsson.cifwk.netsim.test.cases;

import javax.inject.Inject;

import org.testng.annotations.BeforeSuite;
import org.testng.annotations.Test;

import com.ericsson.cifwk.netsim.MiniLinkUnitTestOperator;
import com.ericsson.cifwk.netsim.UnitTestOperator;
import com.ericsson.cifwk.netsim.UnitTestOperatorInterface;
import com.ericsson.cifwk.taf.TestCase;
import com.ericsson.cifwk.taf.TorTestCaseHelper;
import com.ericsson.cifwk.taf.annotations.Context;
import com.ericsson.cifwk.taf.annotations.DataDriven;
import com.ericsson.cifwk.taf.annotations.Input;
import com.ericsson.cifwk.taf.annotations.Output;
import com.ericsson.cifwk.taf.annotations.TestId;
import com.ericsson.cifwk.taf.guice.OperatorRegistry;

/**
 * Executes scripts and verify expected output
 */
public class UnitTest extends TorTestCaseHelper implements TestCase {

	@Inject
	OperatorRegistry<UnitTestOperator> operatorRegistry;
	@Inject
	OperatorRegistry<MiniLinkUnitTestOperator> mloperatorRegistry;

	@BeforeSuite
	public void initialise() {
		assertTrue(new UnitTestOperator().initialise());
		assertTrue(new MiniLinkUnitTestOperator().initialise());
	}

	
	/**
	 * Executes scripts on a remote server which defined in host.properties
	 * file.
	 * 
	 * @DESCRIPTION Verify the script executions
	 * @PRE Copy the scripts to remote server be tested
	 * @VUsers 1
	 * @PRIORITY HIGH Note: NETSUP-2838 Check html report for full explanation
	 *           behind failures
	 */
	@TestId(id = "genstatsreport", title = "Verify the unit test executions")
	@Test(groups = { "Acceptance" })
	@DataDriven(name = "UnitTest")
	@Context(context = { Context.CLI })
	public void verifyGenstatUnitTest(@Input("command") final String command,@Output("expectedExitCode") final int expectedExitCode) {
		String id = null;
		if (command.contains("limitbw")){
			id = "genstatsreport";
			final UnitTestOperatorInterface seOperator = operatorRegistry.provide(UnitTestOperator.class);
			final int scriptExecutionExitCode = seOperator.verifyUnitTestScriptExecution(id, command);
			final boolean testCondition = scriptExecutionExitCode == expectedExitCode;
			if (!testCondition) {
				throw new TestCaseException("Returned exit code: " + scriptExecutionExitCode + ",  while expecting exit code: " + expectedExitCode);
			}
			assertTrue(testCondition);
		} else if (command.contains("confGenerator.py")){
			String[] idArry = {"minilink_indoor", "switch", "outdoor", "fronthaul"};
			for (String myId : idArry){
				final UnitTestOperatorInterface seOperator = mloperatorRegistry.provide(MiniLinkUnitTestOperator.class);
				final int scriptExecutionExitCode = seOperator.verifyUnitTestScriptExecution(myId, command); 
				final boolean testCondition = scriptExecutionExitCode == expectedExitCode;
				if (!testCondition) {
					throw new TestCaseException("Returned exit code: " + scriptExecutionExitCode + ",  while expecting exit code: " + expectedExitCode);
				}
				assertTrue(testCondition);
			}
			
		}
	}
	
}


