/**
 * 【功能说明】
 *   定义一个线程类，从 BufferedReader 中读取所有单词到数组中，使用快速排序算法按字典序排序，
 *   然后将排序后的单词逐行通过 PrintWriter 输出。本类配合 RhymingWords.java（主程序）
 *   和 ReverseThread.java（反转线程）实现"押韵词"流水线处理中的排序阶段。
 *
 * 【知识点】
 *   1. 继承 Thread：自定义排序线程，重写 run() 方法定义排序处理逻辑。
 *   2. 快速排序 (QuickSort)：经典的 O(n log n) 排序算法，采用分治策略实现。
 *   3. 数组存储：将所有输入行读入 String 数组，在内存中完成排序后再输出。
 *   4. String.compareTo()：按字典序（Unicode 编码顺序）比较两个字符串的大小。
 *   5. 三分取中法：快速排序选择数组中间位置的元素作为基准值 (mid)。
 *   6. 递归实现：快速排序通过递归调用自身处理左右两个子分区。
 *   7. 线程间通信：通过管道流与上下游线程交换数据，实现流水线并行处理。
 */
package chp7_io.exp7_3;                      // 声明包路径，位于 chp7_io 实验包下的 exp7_3 子包中

import java.io.BufferedReader;               // 导入 BufferedReader 类，带缓冲的字符输入流，提供高效 readLine() 方法
import java.io.IOException;                  // 导入 IOException 类，用于处理输入/输出操作中发生的异常
import java.io.PrintWriter;                  // 导入 PrintWriter 类，格式化字符输出流，提供 println() 便捷方法

public class SortThread extends Thread {     // 定义 SortThread 类，继承自 Thread，成为一个自定义线程类

    private PrintWriter out = null;          // 声明 PrintWriter 类型成员变量 out（输出流），初始化为 null
    private BufferedReader in = null;        // 声明 BufferedReader 类型成员变量 in（输入流），初始化为 null

    /**
     * 构造函数：接收输入/输出流对象
     * @param out  输出流，用于写入排序后的单词
     * @param in   输入流，用于读取待排序的原始单词
     */
    public SortThread(PrintWriter out, BufferedReader in) {  // 带参构造函数，接收输入/输出流
        this.out = out;                     // 将参数 out 赋值给成员变量 this.out
        this.in = in;                       // 将参数 in 赋值给成员变量 this.in
    }                                       // 构造函数结束

    // 重写 Thread 类的 run() 方法，定义线程的执行体
    public void run() {                     // 当线程 start() 后 JVM 自动调用此方法
        int MAXWORDS = 50;                  // 定义常量 MAXWORDS = 50，表示数组最多能存储 50 个单词

        if (out != null && in != null) {    // 检查输入流和输出流是否都已正确初始化
            try {                           // try 块开始，捕获可能抛出的 IOException
                String[] listOfWords = new String[MAXWORDS];  // 创建长度为 50 的 String 数组，用于存储读取到的所有单词
                int numwords = 0;                              // 声明整型变量 numwords，记录实际读取的单词数量

                while ((listOfWords[numwords] = in.readLine()) != null)  // 逐行读取，将每行存入数组；readLine() 返回 null 表示读取完毕
                    numwords++;                                  // 每成功读取一行，单词计数加 1
                quicksort(listOfWords, 0, numwords-1);           // 调用快速排序方法，对数组中的 [0, numwords-1] 范围进行排序
                for (int i = 0; i < numwords; i++)               // 遍历排序后的数组
                    out.println(listOfWords[i]);                  // 将每个单词逐行输出到 PrintWriter 中
                out.close();                                      // 所有单词输出完毕后关闭输出流
            } catch (IOException e) {                             // 捕获 IO 操作中发生的异常
                System.err.println("SortThread run: " + e);       // 将异常信息打印到标准错误输出流
            }                                                     // catch 块结束
        }                                                         // if 语句结束
    }                                                             // run() 方法结束

    /**
     * 快速排序的静态工具方法（私有），按字典序对字符串数组进行排序
     * @param a   待排序的字符串数组
     * @param lo0 排序范围的左边界索引
     * @param hi0 排序范围的右边界索引
     */
    private static void quicksort(String[] a, int lo0, int hi0) {  // 私有静态快速排序方法
        int lo = lo0;                         // 局部变量 lo，初始化为左边界（用于从左侧扫描的指针）
        int hi = hi0;                         // 局部变量 hi，初始化为右边界（用于从右侧扫描的指针）

        if (lo >= hi)                         // 基线条件：如果左指针 >= 右指针，说明子数组最多只有一个元素
            return;                           // 直接返回，无需排序（递归终止）

        String mid = a[(lo + hi) / 2];        // 选择中间位置的元素作为基准值 (pivot)，用于分区比较
        while (lo < hi) {                     // 外层循环：当左右指针未相遇时继续分区
            while (lo<hi && a[lo].compareTo(mid) < 0)  // 左指针向右移动，跳过所有小于基准值的元素（保持原位）
                lo++;                         // 左指针递增
            while (lo<hi && a[hi].compareTo(mid) > 0)  // 右指针向左移动，跳过所有大于基准值的元素（保持原位）
                hi--;                         // 右指针递减
            if (lo < hi) {                    // 如果左指针仍在右指针左侧（找到了一对需交换的元素）
                String T = a[lo];              // 将左指针指向的元素暂存到临时变量 T 中
                a[lo] = a[hi];                 // 将右指针指向的元素赋值给左指针位置
                a[hi] = T;                     // 将暂存的元素赋值给右指针位置（完成交换）
                lo++;                          // 交换后左指针向中间移动一位
                hi--;                          // 交换后右指针向中间移动一位
            }                                  // if 语句结束
        }                                      // 外层 while 循环结束

        if (hi < lo) {                         // 如果扫描结束后右指针跑到左指针左侧（通常发生在奇数次交换后）
            int T = hi;                        // 交换 hi 和 lo，确保 hi <= lo 用于下一步递归的边界划分
            hi = lo;                           // 将 lo 赋值给 hi
            lo = T;                            // 将原 hi 赋值给 lo（相当于将两指针调换回正确顺序）
        }                                      // if 语句结束

        quicksort(a, lo0, lo);                 // 递归排序左半部分：从 lo0 到 lo（所有 <= 基准值的元素）
        quicksort(a, lo == lo0 ? lo+1 : lo, hi0);  // 递归排序右半部分：处理剩余元素。若 lo 未移动则从 lo+1 开始

    }                                              // quicksort 方法结束

}                                                  // SortThread 类结束
