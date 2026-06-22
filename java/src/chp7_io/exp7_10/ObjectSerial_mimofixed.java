/**
 * 【功能说明】
 *   演示自定义序列化机制。定义了一个 Employee 类实现 Serializable 接口，
 *   自定义了 writeObject() 和 readObject() 方法，在序列化/反序列化时执行自定义逻辑。
 *   序列化时将当前年份写入文件；反序列化时读取保存的年份，与当前年份做差，自动更新员工年龄。
 *   展示了如何精确控制 Java 对象的序列化和反序列化过程。
 *
 * 【知识点】
 *   1. Serializable 接口：标记接口（不含任何方法），标识类可以被序列化。
 *   2. 自定义 writeObject(ObjectOutputStream)：私有方法，替代默认序列化逻辑，精确控制写入哪些字段。
 *   3. 自定义 readObject(ObjectInputStream)：私有方法，替代默认反序列化逻辑，可执行额外的初始化逻辑。
 *   4. writeInt() / writeUTF()：ObjectOutputStream 提供的方法，写入基本类型数据和 UTF 字符串。
 *   5. readInt() / readUTF()：ObjectInputStream 提供的方法，读取基本类型数据和 UTF 字符串。
 *   6. 年龄自动更新：序列化时保存当前年份，反序列化时计算当前年份与保存年份之差，自动增加员工年龄。
 *   7. toString() 覆写：覆写 Object 类的 toString() 方法，提供员工信息的格式化输出。
 *   8. 序列化版本：虽然未显式定义 serialVersionUID，但 JVM 会根据类结构自动生成。
 *   9. 类型转换：反序列化时使用 (Employee) fin1.readObject() 将 Object 转换为 Employee 类型。
 */
package chp7_io.exp7_10;                     // 声明包路径，位于 chp7_io 实验包下的 exp7_10 子包中

import java.io.FileInputStream;              // 导入 FileInputStream 类，文件字节输入流，从文件读取字节数据
import java.io.FileOutputStream;             // 导入 FileOutputStream 类，文件字节输出流，向文件写入字节数据
import java.io.IOException;                  // 导入 IOException 类，处理输入/输出操作异常
import java.io.ObjectInputStream;            // 导入 ObjectInputStream 类，对象输入流，从字节流中反序列化恢复对象
import java.io.ObjectOutputStream;           // 导入 ObjectOutputStream 类，对象输出流，将对象序列化写入字节流
import java.io.Serializable;                 // 导入 Serializable 接口，标记接口，实现该接口的类才能被序列化
import java.util.Calendar;                   // 导入 Calendar 类，用于获取当前年份（替代废弃的Date.getYear()）
import java.util.Date;                       // 导入 Date 类，用于获取当前日期时间（此处用于计算年龄增长）

class Employee_mimofixed implements Serializable {     // 定义 Employee 类，实现 Serializable 接口使其可被序列化
    int id;                                   // 员工编号
    String name;                              // 员工姓名
    int age;                                  // 员工年龄
    int salary;                               // 员工薪水
    String hireDay;                           // 入职日期（字符串格式）
    String department;                        // 所属部门

    public Employee_mimofixed() {}                      // 默认无参构造方法（反序列化时可能需要）

    public Employee_mimofixed(int id, String name, int age, int salary,   // 带参构造方法
                    String hireDay, String department) {        // 初始化所有字段
        this.id = id;                          // 设置员工编号
        this.name = name;                      // 设置员工姓名
        this.age = age;                        // 设置员工年龄
        this.salary = salary;                  // 设置员工薪水
        this.hireDay = hireDay;                // 设置入职日期
        this.department = department;          // 设置所属部门
    }                                          // 构造函数结束

    /**
     * 自定义序列化方法：在序列化时额外保存当前年份，用于后续自动更新年龄
     * writeObject 的签名必须是 "private void writeObject(ObjectOutputStream out)"，
     * JVM 通过反射自动调用此方法替代默认序列化逻辑。
     */
    private void writeObject(ObjectOutputStream out) throws IOException {  // 自定义序列化方法（私有，JVM 自动调用）
        Calendar cal = Calendar.getInstance();         // 获取当前日期时间（此时为序列化时间）

        out.writeInt(id);                        // 手动写入员工编号（int 类型，4 字节）
        out.writeInt(age);                       // 手动写入员工年龄（int 类型）
        out.writeUTF(name);                      // 手动写入员工姓名（UTF-8 编码字符串）
        out.writeInt(salary);                    // 手动写入员工薪水（int 类型）
        out.writeUTF(hireDay);                   // 手动写入入职日期（UTF-8 字符串）
        out.writeUTF(department);                // 手动写入所属部门（UTF-8 字符串）
        out.writeInt(cal.get(Calendar.YEAR));       // 额外写入当前年份（使用Calendar替代废弃的Date.getYear()）
    }                                            // writeObject 方法结束

    /**
     * 自定义反序列化方法：在反序列化时读取保存的年份，自动计算并更新员工年龄
     * readObject 的签名必须是 "private void readObject(ObjectInputStream in)"，
     * JVM 通过反射自动调用此方法替代默认反序列化逻辑。
     */
    private void readObject(ObjectInputStream in) throws IOException {   // 自定义反序列化方法（私有，JVM 自动调用）
        Calendar cal = Calendar.getInstance();         // 获取当前日期时间（此时为反序列化时间）
        int savedYear;                           // 声明变量用于存储序列化时保存的年份

        id = in.readInt();                       // 读取员工编号（必须与写入顺序一致）
        age = in.readInt();                      // 读取员工年龄
        name = in.readUTF();                     // 读取员工姓名
        salary = in.readInt();                   // 读取员工薪水
        hireDay = in.readUTF();                  // 读取入职日期
        department = in.readUTF();               // 读取所属部门
        savedYear = in.readInt();                // 读取序列化时保存的年份

        age = age + (cal.get(Calendar.YEAR) - savedYear);  // 自动更新年龄：原年龄 +（当前年份 - 保存年份），使用Calendar替代废弃的Date.getYear()
    }                                            // readObject 方法结束

    /**
     * 覆写 toString() 方法，返回员工信息的格式化字符串
     * @return 包含所有员工字段的字符串
     */
    public String toString() {                   // 覆写 Object 类的 toString() 方法
        return "id: " + id + "\n name:  " + name + " \n age: "   // 拼接员工编号、姓名
                        + age + "\n salary:  " + salary + "\n hireDay: "    // 拼接年龄、薪水、入职日期
                        + hireDay + "\n department: " + department ;        // 拼接部门信息
    }                                            // toString 方法结束

}                                                // Employee 类结束

/**
 * 【功能说明】
 *   主程序类，演示 Employee 对象的序列化和反序列化过程：
 *   1. 创建一个 Employee 对象
 *   2. 将其序列化写入文件 data1.ser
 *   3. 从文件中反序列化恢复 Employee 对象
 *   4. 输出恢复后的员工信息（注意年龄已自动更新）
 *
 * 【知识点】
 *   1. 自定义序列化：配合 Employee 类中的 writeObject/readObject 自定义方法。
 *   2. ObjectOutputStream(ObjectOutputStream)：创建对象输出流，包装 FileOutputStream。
 *   3. ObjectInputStream(ObjectInputStream)：创建对象输入流，包装 FileInputStream。
 *   4. 序列化/反序列化完整流程：writeObject -> readObject 验证数据完整性。
 *   5. 类引用关系：一个文件可包含多个类（最多一个 public 类），Employee 作为包可见辅助类。
 */
public class ObjectSerial_mimofixed {                  // 定义 ObjectSerial 公有类（对象序列化主程序）

    public static void main(String args[]) throws IOException,   // 程序入口 main 方法
            ClassNotFoundException {                             // 声明可能抛出的异常

        // ========== 序列化部分：创建 Employee 对象并写入文件 ==========
        Employee_mimofixed employ = new Employee_mimofixed(123456, "Tom", 23, 6000, "03/10/10", "intel");
        // 创建一个 Employee 对象：编号 123456，姓名 Tom，年龄 23，薪水 6000，入职日期 2010/03/10，部门 intel

        ObjectOutputStream fout1 = new ObjectOutputStream(         // 创建 ObjectOutputStream
                                        new FileOutputStream("src\\chp7_io\\exp7_10\\data1.ser"));  // 包装 FileOutputStream，输出到 data1.ser
        fout1.writeObject(employ);          // 序列化 Employee 对象（自动调用 Employee 类中自定义的 writeObject 方法）
        fout1.close();                      // 关闭 ObjectOutputStream，释放资源并刷新缓冲区

        // ========== 反序列化部分：从文件中恢复 Employee 对象 ==========
        employ = null;                      // 将原引用置空，便于垃圾回收，验证反序列化后重新创建对象

        ObjectInputStream fin1 = new ObjectInputStream(             // 创建 ObjectInputStream
                                            new FileInputStream("src\\chp7_io\\exp7_10\\data1.ser"));  // 包装 FileInputStream，读取 data1.ser
        employ = (Employee_mimofixed) fin1.readObject();  // 反序列化恢复 Employee 对象（自动调用自定义的 readObject 方法）
        fin1.close();                       // 关闭 ObjectInputStream，释放资源

        System.out.println(employ.toString());  // 输出恢复后的员工信息（年龄已根据年份差值自动更新）

    }                                       // main 方法结束

}                                           // ObjectSerial 类结束
