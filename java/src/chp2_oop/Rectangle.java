package chp2_oop;

class Rectangle {
	private int l, w;

	int perimeter() {
		return 2 * (l + w);
	}

	int area() {
		return l * w;
	}

	Rectangle(int l, int w) {
		this.l = l;
		this.w = w;
	}
}
