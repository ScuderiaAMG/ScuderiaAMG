package chp5_advanced.exp5_6;

import chp5_advanced.exp5_6.graphics.twoD.Point;
import chp5_advanced.exp5_6.graphics.twoD.Rectangle;

public class TestPackage {
	public static void main(String args[]) {
		Point p = new Point(2, 3);
		Rectangle r = new Rectangle(p, 10, 10);
		System.out.println("The area of the rectangle is " + r.area());
	}
}