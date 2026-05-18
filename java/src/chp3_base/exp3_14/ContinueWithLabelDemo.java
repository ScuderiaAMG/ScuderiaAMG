package chp3_base.exp3_14;
public class ContinueWithLabelDemo {
	public static void main(String[] args) {
		String searchMe = "Look for a substring in me";
		String subString = "sub";
		boolean foundIt = false;
		int max = searchMe.length() - subString.length();
		test: for (int i = 0; i < max; i++) {
			int n = subString.length();
			int j = i;
			int k = 0;
			while (n-- != 0) {
				if (searchMe.charAt(j++) != subString.charAt(k++)) {
					continue test;
				}
			}
			foundIt = true;
			break test;
		}
		System.out.println(foundIt ? "Found it" : "Didn't find it");
	}
}
