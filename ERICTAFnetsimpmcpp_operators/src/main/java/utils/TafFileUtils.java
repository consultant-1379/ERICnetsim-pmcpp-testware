/**
 * -----------------------------------------------------------------------
 *     Copyright (C) 2015 LM Ericsson Limited.  All rights reserved.
 * -----------------------------------------------------------------------
 */
package utils;

import java.io.File;
import java.io.FileNotFoundException;
import java.nio.file.Paths;
import java.util.List;
import java.util.regex.Pattern;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.ericsson.cifwk.taf.utils.FileFinder;

/**
 * A taf utility class to get file locations independent from module location
 *
 * @author qfatonu
 *
 */
/**
 * @author qfatonu
 *
 */
public class TafFileUtils {

    /** Logging utility */
    private static final Logger logger = LoggerFactory.getLogger(TafFileUtils.class);

    /**
     * A non instantiable utility class only
     */
    private TafFileUtils() {
    }

    /**
     * Gets full path of given file or folder in String format.
     *
     * @param localFile
     *            relative part of the file or folder name
     * @return absolute path of file or folder
     * @throws FileNotFoundException
     *             if file or folder cannot be found at given path
     */
    public static String getFilePath(final String localFile) throws FileNotFoundException {
        final String initialLocation = System.getProperty("user.dir");
        logger.debug("initialLocation for search to begin: {}", initialLocation);

        final List<String> foundFiles = FileFinder.findFile(localFile);
        logger.debug("foundFiles: {}", foundFiles);

        if (foundFiles == null || foundFiles.isEmpty()) {
            throw new FileNotFoundException(String.format("File '%s' not found", localFile) + "\n initialLocation for search to begin: "
                    + initialLocation);
        }
        return Paths.get(foundFiles.get(0)).toString().replace("\\", "/");
    }

    /**
     * Gets full path of given file or folder in String format after filtered with passed regular expression.
     *
     * @param localFile
     *            relative part of the file or folder name
     * @param regExp
     *            regular expression to be applied on found files
     * @return absolute path of file or folder
     * @throws FileNotFoundException
     *             if file or folder cannot be found at given path
     */
    public static String getFilePath(final String localFile, final String regExp) throws FileNotFoundException {
        final String initialLocation = System.getProperty("user.dir");
        logger.debug("getFilePath-initialLocation for search to begin: {}", initialLocation);

        final List<String> foundFiles = FileFinder.findFile(localFile);
        logger.debug("foundFiles: {}", foundFiles);

        if (foundFiles == null || foundFiles.isEmpty()) {
            throw new FileNotFoundException(String.format("File '%s' not found", localFile) + "\n initialLocation for search to begin: "
                    + initialLocation);
        }
        for (final String file : foundFiles) {
            if (Pattern.compile(regExp).matcher(file).find()) {
                return Paths.get(file).toString().replace("\\", "/");
            }
        }
        return "";
    }

    /**
     * Gets new file(or folder) path based on baseLocation
     *
     * @param baseLocation
     *            relative base location to new file
     * @param newFile
     *            new file where to be put under baseLocation
     * @return absolute path of new file(or folder)
     * @throws FileNotFoundException
     *             if file or folder cannot be found at given path
     */
    public static String getNewFilePath(final String baseLocation, final String newFile) throws FileNotFoundException {
        final String initialLocation = System.getProperty("user.dir");
        logger.debug("getNewFilePath-initialLocation for search to begin: {}", initialLocation);

        final List<String> foundFiles = FileFinder.findFile(baseLocation);
        if (foundFiles == null || foundFiles.isEmpty()) {
            throw new FileNotFoundException(String.format("File '%s' not found", baseLocation) + "\n initialLocation for search to begin: "
                    + initialLocation);
        }
        return Paths.get(foundFiles.get(0)).toString().replace("\\", "/") + "/" + newFile;
    }

    /**
     * Gets parent project dir in maven modularized projects based on parent project name.
     *
     * @return main project directory for modularized maven projects
     */
    public static String getProjectBaseDir() {
        final String projectBaseDir = System.getProperty("user.dir");
        logger.debug("projectBaseDir(user.dir):{}", projectBaseDir);
        final File projectBaseDirFile = new File(projectBaseDir);
        if (Pattern.compile("testware").matcher(projectBaseDir).find()) {
            if (!projectBaseDir.endsWith("testware")) {
                return projectBaseDirFile.getParent();
            }
        }
        return projectBaseDir;
    }

    public static void main(final String[] args) {
        try {
            System.out.println("scripts:" + TafFileUtils.getFilePath("ScriptExecutionOperator.java"));
        } catch (final Exception e) {
            logger.error("Error in TafFileUtils: ", e);
        }
    }

}
