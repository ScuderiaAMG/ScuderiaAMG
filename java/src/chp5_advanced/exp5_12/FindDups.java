/**
 * 【功能说明】
 * 本程序演示了Java中Set集合的使用，特别是HashSet的去重功能。
 * 程序从命令行参数接收多个字符串，将它们逐一添加到HashSet中。
 * HashSet的特性是自动去除重复元素——如果添加了已存在的元素，
 * add()方法返回false。程序最终输出去重后的不重复单词数量及内容。
 *
 * 【知识点】
 * 1. Set接口：不包含重复元素的集合，与数学中的"集合"概念对应
 * 2. HashSet类：基于哈希表实现的Set，具有高效的查找性能（O(1)）
 * 3. Set.add()方法：如果元素尚未存在则添加并返回true，否则返回false
 * 4. 泛型Set<String>：指定集合中只能存放String类型的元素
 * 5. 默认初始容量：HashSet默认初始容量为16，负载因子0.75
 * 6. 增强的for-each虽未使用，但size()方法返回集合中元素个数
 * 7. 数组的length属性：args.length获取命令行参数个数
 */
package chp5_advanced.exp5_12;                             // 声明包路径，该文件位于chp5_advanced.exp5_12包中

import java.util.HashSet;                                  // 导入HashSet类，基于哈希表的Set实现
import java.util.Set;                                      // 导入Set接口

public class FindDups {                                    // 主类（public），用于查找命令行参数中的重复单词
    public static void main(String args[]) {               // 主方法：程序执行的入口点，args为命令行参数数组
        Set<String> s = new HashSet<String>();             // 创建一个HashSet集合，默认初始容量为16，只存放String类型的元素

        for (int i = 0; i < args.length; i++) {            // 遍历命令行参数数组中的所有字符串
            // 尝试将当前字符串添加到集合中，如果添加失败（返回false）说明该字符串已存在（重复）
            if (!s.add(args[i]))                           // add()方法：如果集合中已存在该元素则返回false，否则添加并返回true
                System.out.println("Duplicate detected: " + args[i]); // 输出重复的单词
        }

        System.out.println(s.size() + " distinct words detected: " + s); // 输出不重复单词的数量以及集合中的所有元素
    }
}
