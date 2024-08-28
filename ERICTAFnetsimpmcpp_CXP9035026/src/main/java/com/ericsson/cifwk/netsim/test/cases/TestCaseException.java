/**
 * -----------------------------------------------------------------------
 *     Copyright (C) 2015 LM Ericsson Limited.  All rights reserved.
 * -----------------------------------------------------------------------
 */
package com.ericsson.cifwk.netsim.test.cases;

/**
 * Test case exception thrown by test cases.
 *
 * @author qfatonu
 *
 */
public class TestCaseException extends RuntimeException {

    private static final long serialVersionUID = 1L;

    /**
     * Constructs a new runtime test case exception
     */
    public TestCaseException() {
        super("TestCaseException");
    }

    /**
     * Constructs a new runtime test case exception with detail message
     *
     * @param message
     *            the detail message
     */
    public TestCaseException(final String message) {
        super(message);
    }

}
