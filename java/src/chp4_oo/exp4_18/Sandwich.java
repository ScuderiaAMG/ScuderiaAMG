package chp4_oo.exp4_18;
class Meal {
	static int i=10;
	static {
		System.out.println(++i);
		}
	Meal() {
		System.out.println("Meal()");
	}
}
class Bread {
	Bread() {
		System.out.println("Bread()");
	}
}
class Cheese {
	Cheese() {
		System.out.println("Cheese()");
	}
}
class Lettuce {
	Lettuce() {
		System.out.println("Lettuce()");
	}
}
class Lunch extends Meal {
	Lunch() {
		System.out.println("Lunch()");
	}
}
class PortableLunch extends Lunch {
	PortableLunch() {
		System.out.println("PortableLunch()");
	}
}
public class Sandwich extends PortableLunch {
	private Bread b = new Bread();
	private Cheese c = new Cheese();
	private Lettuce l = new Lettuce();
	public Sandwich() {
		System.out.println("Sandwich()");
	}
	static {
		System.out.println("Static statement");
		new Sandwich();
	}
	public static void main(String[] args) {
		new Sandwich();
	}
}
