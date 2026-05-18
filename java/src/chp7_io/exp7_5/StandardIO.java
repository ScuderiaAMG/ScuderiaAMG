package chp7_io.exp7_5;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class StandardIO {
	public static void main(String[] args) throws IOException {
		int i=0;
		boolean flag;
		String s;
		BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
		System.out.println("请输入（exit退出）：");
		try {
			s = in.readLine();
			while (!s.equals("exit")) {
				try {
					flag=false;
					i = Integer.parseInt(s);
				} catch (NumberFormatException e) {
					flag=true;
					System.out.println("您刚输入的是：" + s);
				}
				if(flag==false){System.out.println("整数：" + i);}
				s = in.readLine();
			}
			System.out.println("输入完毕！");
			in.close();
		} finally {
		}
	}
}