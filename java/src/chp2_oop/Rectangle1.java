//面向过程
package chp2_oop;

class Rectangle1 {
	static int perimeter(int length, int width) {
		return 2 * (length + width);
	}

	static int area(int length, int width) {
		return length * width;
	}

	public static void main(String[] args) {
		System.out.println("perimeter = " + Rectangle1.perimeter(5, 4));
		System.out.println("area = " + Rectangle1.area(5, 4));
	}
}
