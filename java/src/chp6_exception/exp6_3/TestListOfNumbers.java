package chp6_exception.exp6_3;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
class ListOfNumbers {
    private ArrayList<Integer> list;
    private static final int size = 10;
    public ListOfNumbers () {
        list = new ArrayList<Integer>(size);
        for (int i = 0; i < size; i++)
            list.add(new Integer(i));
    }
    public void writeList() {
        PrintWriter out = null;
        try {
            System.out.println("Entering try statement");
            out = new PrintWriter(new FileWriter("OutFile.txt"));
            for (int i = 0; i < size; i++){
                out.println("Value at: " + i + " = " + list.get(i));
            }
        } catch (IndexOutOfBoundsException e) { //处理越界异常。
            System.err.println("Caught IndexOutOfBoundsException: " +
				 e.getMessage());
        } catch (IOException e) {  //处理I/O异常。
            System.err.println("Caught IOException: " + e.getMessage());
        } finally {  //最后清理。
            if (out != null) {
                System.out.println("Closing PrintWriter");
                out.close();
            } else {
                System.out.println("PrintWriter not open");
            }
          }       
    }
}
public class TestListOfNumbers {
    public static void main(String[] args) {
	ListOfNumbers list = new ListOfNumbers();
	list.writeList();
    }
}
