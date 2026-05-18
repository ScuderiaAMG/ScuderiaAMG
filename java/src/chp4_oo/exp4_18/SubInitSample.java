package chp4_oo.exp4_18;

public class SubInitSample {
	public static void main(String[] args) { new B(); }
	private static class A {
		public static C c = new C("A");
		static { System.out.println("A类static块"); }
		public A() { System.out.println("A的构造方法"); }
		{ System.out.println("A类普通块"); }
	}
	private static class B extends A {
		public static C c = new C("B");
		static { System.out.println("B类static块"); }
		{ System.out.println("B类普通块"); }
		public B() { System.out.println("B的构造方法"); }
	}
	private static class C {
		String id;
		public C(String id) {
			this.id = id;
			System.out.println(this.id + "调用C的构造方法 "); }
	}
}