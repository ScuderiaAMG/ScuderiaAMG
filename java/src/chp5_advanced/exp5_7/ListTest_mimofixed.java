/**
 * 【功能说明】
 * 本程序演示了Java泛型出现之前的集合类使用方式（原始类型/Raw Type）。
 * 使用没有泛型参数的LinkedList集合，可以添加任意类型的对象，
 * 但在取出时需要进行强制类型转换（向下转型）。如果类型不匹配，
 * 将在运行时抛出ClassCastException异常，这是一个潜在的安全隐患。
 *
 * 【知识点】
 * 1. 原始类型集合（Raw Type）：不使用泛型的集合，可以存放任意Object类型
 * 2. 自动装箱（Auto-boxing）：new Integer(2000)手动创建Integer对象
 *    （JDK 5之前需要手动装箱，JDK 5之后支持自动装箱）
 * 3. 向下转型（Downcasting）：从Object类型强制转换为具体的Integer类型
 * 4. 类型不安全：集合中可以混入不同类型的数据（如第9行混入String），编译期无法检测
 * 5. 运行时异常：ClassCastException在运行时抛出，程序可能崩溃
 * 6. 这正是泛型（Generics）引入的原因——提供编译期类型安全检查
 */
package chp5_advanced.exp5_7;                              // 声明包路径，该文件位于chp5_advanced.exp5_7包中

import java.util.LinkedList;                               // 导入LinkedList类，用于创建链表集合
import java.util.List;                                     // 导入List接口，作为集合的引用类型

public class ListTest_mimofixed {                                    // 主类（public），演示原始类型集合的使用
    public static void main(String[] args) {               // 主方法：程序执行的入口点
        // 注意：列表中只应存放Integer类型的对象
        List<Object> listofInteger = new LinkedList<Object>();             // 使用泛型参数<Object>创建LinkedList，明确指定类型参数
        listofInteger.add(Integer.valueOf(2000));              // 向集合中添加一个Integer对象（值为2000），使用valueOf替代废弃的构造函数
        listofInteger.add("8");                            // 向集合中添加一个String对象"8"（编译通过，但破坏了类型一致性）
        Integer x = (Integer) listofInteger.get(0);        // 取出索引0处的元素，需要手动强制转换为Integer类型（此处类型正确，转换成功）
        System.out.println(x);                             // 输出整数x的值：2000
        x = (Integer) listofInteger.get(1);               // 取出索引1处的元素，强制转换为Integer类型（运行时抛出ClassCastException异常！因为实际是String类型）
        System.out.println(x);                             // 此行因上面的异常而不会被执行
    }
}
