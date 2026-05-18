package chp5_advanced.exp5_14;
import java.util.LinkedList;
import java.util.Queue;
public class Counter {
    public static void main(String[] args){
        int time = 5;
        Queue<Integer> queue = new LinkedList<Integer>();
        for (int i = time; i >= 0; i--)
            queue.add(i);
        while (!queue.isEmpty()) {
            System.out.println("    "+queue.remove());
            try{
            	Thread.sleep(1000);
            }catch(InterruptedException e){ }
        }
    }
}
