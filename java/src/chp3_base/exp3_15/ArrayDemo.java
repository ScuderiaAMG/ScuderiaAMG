package chp3_base.exp3_15;
public class ArrayDemo {
	public static void main(String[] args) {
		int[] anArray;			//声明一个整形数组
		anArray = new int[10];	//创建数组
		//给数组每个元素赋值并打印输出
		for (int i = 0; i < anArray.length; i++) {
			anArray[i] = i;
			System.out.print(anArray[i] + " ");
		}
		System.out.println();
	}
}
