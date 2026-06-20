/**
 * 【功能说明】
 * 本程序演示了Java中ListIterator（列表迭代器）的用法。
 * ListIterator比普通的Iterator更强大，支持双向遍历、
 * 在遍历过程中添加（add）、修改（set）、删除（remove）元素。
 * 程序创建了一个ArrayList并添加了1~4四个数字，然后使用
 * ListIterator在列表头部添加0、修改索引1处的元素为9、
 * 删除索引2处的元素，展示了ListIterator的增删改操作。
 *
 * 【知识点】
 * 1. ListIterator接口：继承自Iterator，支持双向遍历的列表专用迭代器
 * 2. ListIterator.add()：在当前迭代位置之前插入元素（游标的概念）
 * 3. ListIterator.set()：替换最后一次调用next()或previous()返回的元素
 * 4. ListIterator.remove()：移除最后一次调用next()或previous()返回的元素
 * 5. ListIterator.nextIndex()：返回下一次调用next()将返回的元素的索引
 * 6. hasNext()：检查是否还有下一个元素可遍历
 * 7. 游标（Cursor）概念：ListIterator的游标位于元素之间
 * 8. ArrayList：基于动态数组的List实现
 */
package chp5_advanced.exp5_16;                             // 声明包路径，该文件位于chp5_advanced.exp5_16包中

import java.util.ArrayList;                                // 导入ArrayList类
import java.util.List;                                     // 导入List接口
import java.util.ListIterator;                             // 导入ListIterator接口，列表专用迭代器

public class ListIteratorDemo {                            // 主类（public），演示ListIterator的用法
    public static void main(String[] args) {               // 主方法：程序执行的入口点
        List<Integer> list = new ArrayList<Integer>();     // 创建一个ArrayList列表，泛型参数为Integer
        // 向list中添加元素1~4
        for (int i = 1; i < 5; i++) {                      // 循环变量i从1到4（不包含5）
            list.add(new Integer(i));                      // 将i包装为Integer对象后添加到列表末尾（list变为[1,2,3,4]）
        }
        System.out.println("The original list : " + list); // 输出原始列表内容：[1, 2, 3, 4]

        ListIterator<Integer> listIter = list.listIterator(); // 获取列表的ListIterator迭代器（游标初始位于索引0之前）
        listIter.add(new Integer(0));                      // 在迭代器当前位置（列表头部）之前插入元素0（list变为[0,1,2,3,4]）
        System.out.println("After add at beginning:" + list); // 输出在开头添加元素后的列表：[0, 1, 2, 3, 4]

        if (listIter.hasNext()) {                          // 检查是否还有下一个元素（当前游标位于索引1之前？注意：add后游标位置变了）
            int i = listIter.nextIndex();                  // 获取下一次调用next()将返回的元素的索引（此时i的值为1）
            listIter.next();                               // 移动到下一个元素并返回该元素（即索引为1的元素，原列表中的1）
            listIter.set(new Integer(9));                  // 将刚刚返回的元素（索引1处的元素）修改为9（list变为[0,9,2,3,4]）
            System.out.println("After set at " + i + ":" + list); // 输出修改后的列表：[0, 9, 2, 3, 4]
        }

        if (listIter.hasNext()) {                          // 检查是否还有下一个元素（当前游标位于索引2之前）
            int i = listIter.nextIndex();                  // 获取下一次调用next()将返回的元素的索引（此时i的值为2）
            listIter.next();                               // 移动到下一个元素并返回该元素（即索引为2的元素，原列表中的2）
            listIter.remove();                             // 移除刚刚返回的元素（索引2处的元素被删除，list变为[0,9,3,4]）
            System.out.println("After remove at " + i + " : " + list); // 输出删除元素后的列表：[0, 9, 3, 4]
        }
    }
}
