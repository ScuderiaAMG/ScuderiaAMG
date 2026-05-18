package chp5_advanced.exp5_3;
class StaticInitDemo{
	static int i;
	static {
		i = 5;
		System.out.println("Static code: i="+	i++);
		}
	}
public class TestStaticInit {
	public static void main(String args[]){
		System.out.println(" Main code: i="+ StaticInitDemo.i);
		}
	}
