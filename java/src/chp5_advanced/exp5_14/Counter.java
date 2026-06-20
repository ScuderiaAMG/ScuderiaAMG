/**
 * 【功能说明】
 * 本程序模拟了一个倒计时计数器，演示了Java中Queue（队列）数据结构、
 * LinkedList作为队列实现以及Thread.sleep()线程休眠的用法。
 * 程序将一个从5到0的整数序列放入队列中，然后每隔1秒从队列头部
 * 取出并输出一个元素，模拟倒计时效果。
 *
 * 【知识点】
 * 1. Queue接口：队列，遵循FIFO（先进先出）原则
 * 2. LinkedList作为Queue的实现：LinkedList实现了Queue接口，可作为队列使用
 * 3. Queue.add()：向队列尾部添加元素
 * 4. Queue.remove()：移除并返回队列头部的元素
 * 5. Queue.isEmpty()：判断队列是否为空
 * 6. 异常处理（try-catch）：Thread.sleep()可能抛出InterruptedException
 * 7. Thread.sleep(1000)：使当前线程暂停执行1000毫秒（1秒）
 * 8. 循环递减：for (int i = time; i >= 0; i--) 生成从time到0的递减序列
 */
package chp5_advanced.exp5_14;                             // 声明包路径，该文件位于chp5_advanced.exp5_14包中

import java.util.LinkedList;                               // 导入LinkedList类，可用作队列实现
import java.util.Queue;                                    // 导入Queue接口

public class Counter {                                     // 主类（public），模拟倒计时计数器
    public static void main(String[] args) {               // 主方法：程序执行的入口点
        int time = 5;                                      // 定义倒计时初始值（从5开始倒计时）
        Queue<Integer> queue = new LinkedList<Integer>();  // 创建LinkedList作为Queue实现，泛型参数为Integer
        for (int i = time; i >= 0; i--)                    // 循环：从5递减到0
            queue.add(i);                                  // 将当前数字i添加到队列尾部（队列变为[5,4,3,2,1,0]）
        while (!queue.isEmpty()) {                         // 当队列不为空时，持续取出元素
            System.out.println("    " + queue.remove());   // 移除并输出队列头部的元素（FIFO顺序：5,4,3,2,1,0）
            try {                                          // 异常处理开始
                Thread.sleep(1000);                        // 当前线程休眠1000毫秒（1秒），模拟倒计时的间隔
            } catch (InterruptedException e) {             // 捕获InterruptedException异常（当线程被中断时抛出）
            }                                              // 异常处理体为空（忽略中断异常）
        }
    }
}
