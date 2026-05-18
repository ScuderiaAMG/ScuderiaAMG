package chp7_io.exp7_1;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
public class CopyBytes {
    public static void main(String[] args) throws IOException {
        //创建两个File类对象。
        File outputFile = new File("src\\chp7_io\\exp7_1\\outagainb.txt");
        //创建文件输入/输出字节流。
        FileInputStream in = new FileInputStream("src\\chp7_io\\exp7_1\\farrago.txt");
        FileOutputStream out = new FileOutputStream(outputFile);
        int c;
        //读写文件流中的数据。
        while ((c = in.read()) != -1)
           out.write(c);
        //关闭流。
        in.close();
        out.close();
    }
}
