/**
 * 【功能说明】
 * 本程序演示了Java中Map（映射）接口和TreeMap的使用，
 * 实现了一个单词频率统计器（Word Frequency Counter）。
 * 程序遍历给定的单词数组，使用TreeMap以单词为键（Key）、
 * 出现次数为值（Value）进行统计，最终输出所有不重复的单词
 * 及其出现的频率，单词按字典序排列。
 *
 * 【知识点】
 * 1. Map接口：键值对（Key-Value）映射，每个键最多映射到一个值
 * 2. TreeMap类：基于红黑树（Red-Black Tree）的Map实现，键按自然顺序或比较器排序
 * 3. Map.get(key)：根据键获取对应的值，如果键不存在则返回null
 * 4. Map.put(key, value)：在Map中存储键值对（若键已存在则覆盖旧值）
 * 5. Map.size()：返回Map中键值对的数量
 * 6. 自动装箱/拆箱：Integer与int之间的自动转换
 * 7. 增强for-each循环：用于遍历数组和集合
 * 8. TreeMap的有序性：输出时单词按字典序（字母顺序）排列
 */
package chp5_advanced.exp5_15;                             // 声明包路径，该文件位于chp5_advanced.exp5_15包中

import java.util.Map;                                      // 导入Map接口
import java.util.TreeMap;                                  // 导入TreeMap类，基于红黑树的有序Map

public class Freq {                                        // 主类（public），实现单词频率统计
    public static void main(String args[]) {               // 主方法：程序执行的入口点
        String[] words = {"if", "it", "is", "to", "be", "it", "is", "up", // 定义一个单词数组（包含重复单词）
                          "to", "me", "to", "delegate"};   // 继续：部分单词出现多次（如"to"出现3次）

        Integer freq;                                      // 声明Integer类型变量freq，用于临时存储单词频率
        Map<String, Integer> m = new TreeMap<String, Integer>(); // 创建TreeMap：键为String（单词），值为Integer（频率），自动按字典序排序

        // 遍历单词数组，统计每个单词的出现频率
        for (String a : words) {                           // 增强for-each循环：遍历words数组中的每个单词
            freq = m.get(a);                               // 从Map中获取当前单词的频率（若单词不存在则返回null）

            // 更新频率计数
            if (freq == null) {                            // 如果频率为null，说明该单词第一次出现
                freq = new Integer(1);                     // 初始频率设置为1
            } else {                                       // 否则，该单词已经出现过
                freq = new Integer(freq.intValue() + 1);   // 在原有频率基础上加1（手动拆箱intValue() + 1再装箱）
            }
            m.put(a, freq);                                // 将单词及其更新后的频率存入Map（若键已存在则覆盖旧值）
        }

        System.out.println(m.size() + " distinct words detected:"); // 输出不重复的单词数量（Map中键值对的个数）
        System.out.println(m);                             // 输出整个Map（键值对形式，按单词字典序排列）
    }
}
