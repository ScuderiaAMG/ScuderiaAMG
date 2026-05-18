package chp4_oo.exp4_8;
class Dog {
	String name;
	Dog(String name) {
		this.name = name;
	}
	String getName() {
		return name;
	}
	void setName(String name) {
		this.name = name;
	}
}
public class UseDog {
	public static void main(String[] args) {
		Dog d = new Dog("Íú²Æ");
		d.setName("Ð¡Ç¿");
		System.out.println("The dog's name is "+d.getName());
	}
}
