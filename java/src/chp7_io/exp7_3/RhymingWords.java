package chp7_io.exp7_3;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.PipedReader;
import java.io.PipedWriter;
import java.io.PrintWriter;
import java.io.Reader;

public class RhymingWords {
    public static void main(String[] args) throws IOException {

        FileReader words = new FileReader("src\\chp7_io\\exp7_3\\words.txt");

        // 进行单词的逆序、排序、再逆序还原。
        Reader rhymedWords = reverse(sort(reverse(words)));

        // 将处理后的单词列表输出显示。
        BufferedReader in = new BufferedReader(rhymedWords);
        String input;

        while ((input = in.readLine()) != null)
            System.out.println(input);
        in.close();
    }

    //单词逆序方法。
    public static Reader reverse(Reader source) throws IOException {

        BufferedReader in = new BufferedReader(source);

        PipedWriter pipeOut = new PipedWriter();
        PipedReader pipeIn = new PipedReader(pipeOut);
        PrintWriter out = new PrintWriter(pipeOut);

        new ReverseThread(out, in).start();

        return pipeIn;
    }

   //单词排序方法。
    public static Reader sort(Reader source) throws IOException {

        BufferedReader in = new BufferedReader(source);

        PipedWriter pipeOut = new PipedWriter();
        PipedReader pipeIn = new PipedReader(pipeOut);
        PrintWriter out = new PrintWriter(pipeOut);

        new SortThread(out, in).start();

        return pipeIn;
    }
}
