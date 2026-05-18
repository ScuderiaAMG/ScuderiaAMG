package chp3_base.exp3_17;
public class ArrayOfArraysDemo1 {
	public static void main(String[] args) {
		int[][] aMatrix = new int[4][];// aMatrix指向4个引用组成的元素
		// 创建每个int数组，并进行赋值
		for (int i = 0; i < aMatrix.length; i++) {
			aMatrix[i] = new int[5];
			for (int j = 0; j < aMatrix[i].length; j++) {
				aMatrix[i][j] = i + j;
			}
		}
		// 将数组打印输出
		for (int i = 0; i < aMatrix.length; i++) {
			for (int j = 0; j < aMatrix[i].length; j++) {
				System.out.print(aMatrix[i][j] + " ");
			}
			System.out.println();
		}
	}
}
