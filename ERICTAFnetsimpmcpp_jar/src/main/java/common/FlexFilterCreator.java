package common;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;

/**
 * The Class FlexFilterCreator.
 */
public class FlexFilterCreator {
	
	/** The final filter. */
	private List<String> finalFilter;

	/** The check. */
	private static boolean check;

	/** The MAX. */
	private static final int MAX = 8; 

	/** The ONE. */
	private static final int ONE = 1;

	/** The ZERO. */
	private static final int ZERO = 0;

	/** The THREE. */
	private static final int THREE = 3;

	/** The DASH. */
	private static final String DASH = "-";

	/** The COLON. */
	private static final String COLON = ":";

	/** The TO. */
	private static final String TO = "To";
	
	public static void main(String[] args) {
	    new FlexFilterCreator().processFilters("Plmn:TeCat:EtCat:".split(":"),"0-1:0-1:0-1".split(":"));
	}

	/**
	 * This will process all the filters and will create all possible set from the available filter.
	 *
	 * @param filterList the filter list
	 */
	public List<String> processFilters(String [] filterList, String [] range){
		List<List<String>> powerSet = new LinkedList<List<String>>();
		for (int index = ONE; index <= filterList.length; index++){
	        powerSet.addAll(combination(Arrays.asList(filterList), index));
	    }
		createFilterSet(powerSet,filterList.length);
		return createFilterWithRange(range,filterList);
	}
	
	/**
	 * This will fetch max 8 filters from the filtered list.
	 *
	 * @param powerSet the power set
	 */
	public void createFilterSet(List<List<String>> powerSet, int length){
		List<Integer> uniqueFilterCheck = new ArrayList<Integer>();
		for( Iterator<List<String>> iterate = ((LinkedList<List<String>>) powerSet).descendingIterator(); iterate.hasNext(); ) {
			if(getFinalFilter().size() == MAX){
				check = true;
				break;
			}
		    List<String> filterList = iterate.next();
		    if(!uniqueFilterCheck.contains(filterList.size()) && filterList.size() != ONE){
		    	String filterName = ""; 
		    	for(String filterIndex : filterList){
		    		if(filterName.isEmpty()){
		    			filterName = filterIndex;
		    		}else{
		    			filterName = filterName +COLON+filterIndex;
		    		}
		    	}
		    	if(!getFinalFilter().contains(filterName)){
		    		if(length > THREE){
		    			uniqueFilterCheck.add(filterList.size());
		    		}
		    		getFinalFilter().add(filterName);
		    	}
		    }
		}
		if(!check && powerSet.size() > MAX){
			uniqueFilterCheck.clear();
			createFilterSet(powerSet,length);
		}
	}
	
	/**
	 * This will generate all possible filter combination.
	 *
	 * @param <T> the generic type
	 * @param values the values
	 * @param size the size
	 * @return the list
	 */
	public static <T> List<List<T>> combination(List<T> values, int size) {
	    if (ZERO == size) {
	        return Collections.singletonList(Collections.<T> emptyList());
	    }
	    if (values.isEmpty()) {
	        return Collections.emptyList();
	    }
	    List<List<T>> combinationList = new LinkedList<List<T>>();
	    T actual = values.iterator().next();
	    List<T> subSet = new LinkedList<T>(values);
	    subSet.remove(actual);
	    List<List<T>> subSetCombination = combination(subSet, size - ONE);
	    for (List<T> set : subSetCombination) {
	        List<T> newSet = new LinkedList<T>(set);
	        newSet.add(ZERO, actual);
	        combinationList.add(newSet);
	    }
	    combinationList.addAll(combination(subSet, size));
	    return combinationList;
	}
	
	public List<String> createFilterWithRange(String [] range, String [] filterList){
		List<String> filterWithRange = new ArrayList<String>();
		for(String filter : getFinalFilter()){
			String newValue = filter;
			for(int count=0; count < filterList.length; count++){
				String [] rangValue =  range[count].split(DASH);
				newValue = newValue.replace(filterList[count], filterList[count]+rangValue[0]+TO+rangValue[1]);
			}
			filterWithRange.add(newValue.replaceAll(COLON, ""));
		}
		return filterWithRange;
	}
	
	/**
	 * Gets the final filter.
	 *
	 * @return the final filter
	 */
	public List<String> getFinalFilter() {
		if(null == finalFilter){
			finalFilter = new ArrayList<String>();
			return finalFilter;
		}
		return finalFilter;
	}
}

