package utils;

import java.util.List;

import com.ericsson.cifwk.taf.tools.cli.CLICommandHelper;

public class GenericMethodUtils {

	/*
	 * This method will return String based on availability of file
	 */
	public static String isFileExists(String fileName, CLICommandHelper cliCmdHelper) {
		return removeNewLineCharacter(cliCmdHelper.simpleExec("if [ -f " + fileName + " ]; then echo true; else echo false; fi").trim());
	}
	
	/*
	 * This method will return String based on availability of folder
	 */
	public static String isFolderExists(String folderName, CLICommandHelper cliCmdHelper){
		return removeNewLineCharacter(cliCmdHelper.simpleExec("if [ -d " + folderName + " ]; then echo true; else echo false; fi").trim());
	}

	/*
	 * This method will return simulations list from netsim_cfg file.
	 */
	public static String[] getCfgSimList(String hostname, String cfg_file, CLICommandHelper cliCmdHelper) {
		String serverName = removeNewLineCharacter(cliCmdHelper.simpleExec(hostname).replace("-", "_")) + "_list";
		String[] simList = removeNewLineCharacter(cliCmdHelper.simpleExec("cat " + cfg_file + " | grep " +  serverName + " | cut -d'=' -f2")).replace("\"", "").trim().split(" ");
		return simList;
	}
	
	/*
	 * This method will print the message according to the levels.
	 */
	public static void printMessage(String msg, String level){
		System.out.println("[" + level + "]: " + msg);
	}
	
	/*
	 * This method contains for loop for debuging Array.
	 */
	public static void printArrayData(String[] dataArray){
		for (String data : dataArray){
			System.out.println("printing data : " + data);
		}
	}
	
	/*
	 * This method contains for loop for debuging List.
	 */
	public static void printListData(List<String> dataList){
		for (String data : dataList){
			System.out.println("printing data : " + data);
		}
	}
	
	public static String removeNewLineCharacter(String inputStr){
		return inputStr.replace("\n","").replace("\r", "");
	}
}

