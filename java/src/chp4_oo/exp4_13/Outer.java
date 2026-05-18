package chp4_oo.exp4_13;
class Outer{ 
	private int size=5;
	/** 方法makeInner()，返回一内部类对象 */
	public Object makeInner(final int finalLocalVar){ 
		int localVar=6;
		class Inner{ 
			public String toString(){ 
				return ("#<Inner size="+size+
			    //" localVar=" + localVar + //此处对局部变量localVar的访问非法 
				" finalLocalVar="+finalLocalVar+">");
			}
		}
		return new Inner(); //方法makeInner()返回一内部类对象
	}
	public static void main(String[] args){
		Outer outer=new Outer ();
		Object obj=outer.makeInner(40);
		System.out.println("The object is "+obj.toString());
	}	
}
