package chp2_oop;

public class TestRect {
	public static void main(String[] args) {
		Rectangle rect1 = new Rectangle(10, 5);
		Rectangle rect2 = new Rectangle(6, 4);
		System.out.println("perimeter of rect1 = " + rect1.perimeter());
		System.out.println("area of rect1 = " + rect1.area());
		System.out.println("perimeter of rect2 = " + rect2.perimeter());
		System.out.println("area of rect2 = " + rect2.area());
	}
}
