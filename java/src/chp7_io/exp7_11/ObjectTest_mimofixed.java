/**
 * 【功能说明】
 *   演示 Externalizable 接口的自定义序列化机制，与 Serializable 的对比学习。
 *   EmployeeExtern 类（基类）——普通类，未实现任何序列化接口（本身不可序列化）。
 *   ManagerExtern 类（子类）——继承 EmployeeExtern 并实现 Externalizable 接口，
 *   通过 writeExternal() / readExternal() 方法完全手动控制序列化过程。
 *   与 exp7_10 的 ObjectSerial 对比：Externalizable 需要手动管理所有字段的读写，
 *   而 Serializable 的自定义 writeObject/readObject 是在默认序列化基础上进行调整。
 *
 * 【知识点】
 *   1. Externalizable 接口：继承自 Serializable，但提供了 writeExternal() 和 readExternal() 方法，
 *      实现类需自行管理所有序列化/反序列化逻辑（无默认行为）。
 *   2. writeExternal(ObjectOutput)：手动将对象的字段写入输出流，完全控制写入内容。
 *   3. readExternal(ObjectInput)：手动从输入流读取数据恢复对象字段。
 *   4. 继承与序列化：ManagerExtern 继承 EmployeeExtern，需要手动保存/恢复父类的字段。
 *   5. super()：子类构造方法通过 super() 调用父类构造方法初始化继承的字段。
 *   6. ObjectInput / ObjectOutput：Externalizable 方法接收这两个接口类型（由 ObjectInputStream/ObjectOutputStream 实现）。
 *   7. 无参构造方法：Externalizable 反序列化时需要调用无参构造方法创建对象，再填充字段。
 *      因此 ManagerExtern 和 EmployeeExtern 都必须提供无参构造方法。
 *   8. 路径注意：反序列化时读取 "data2.ser"（相对路径，无子目录）与写入路径不同，
 *      可能因工作目录不同而读取失败，需注意调用时的运行位置。
 */
package chp7_io.exp7_11;                     // 声明包路径，位于 chp7_io 实验包下的 exp7_11 子包中

import java.io.Externalizable;               // 导入 Externalizable 接口，提供更精细的序列化控制（需实现 writeExternal/readExternal）
import java.io.FileInputStream;              // 导入 FileInputStream 类，文件字节输入流，从文件读取字节数据
import java.io.FileOutputStream;             // 导入 FileOutputStream 类，文件字节输出流，向文件写入字节数据
import java.io.IOException;                  // 导入 IOException 类，处理输入/输出操作异常
import java.io.ObjectInput;                  // 导入 ObjectInput 接口，对象输入接口，提供读取对象和基本类型的方法
import java.io.ObjectInputStream;            // 导入 ObjectInputStream 类，对象输入流，从字节流中反序列化恢复对象
import java.io.ObjectOutput;                 // 导入 ObjectOutput 接口，对象输出接口，提供写入对象和基本类型的方法
import java.io.ObjectOutputStream;           // 导入 ObjectOutputStream 类，对象输出流，将对象序列化写入字节流
import java.util.Calendar;                   // 导入 Calendar 类，用于获取当前年份（替代废弃的Date.getYear()）
import java.util.Date;                       // 导入 Date 类，用于获取当前日期时间

class EmployeeExtern_mimofixed {                       // 定义 EmployeeExtern 基类（员工信息类，未实现任何序列化接口）
    // 字段声明：将被显式保存的成员数据
    int id;                                   // 员工编号
    String name;                              // 员工姓名
    int age;                                  // 员工年龄
    int salary;                               // 员工薪水
    String hireDay;                           // 入职日期
    String department;                        // 所属部门

    public EmployeeExtern_mimofixed() {}                // 默认无参构造方法（Externalizable 反序列化时必需）

    EmployeeExtern_mimofixed(int id, String name, int age, int salary, String hireDay,   // 带参构造方法
                    String department) {                                       // 初始化所有字段
        this.id = id;                          // 设置员工编号
        this.name = name;                      // 设置员工姓名
        this.age = age;                        // 设置员工年龄
        this.salary = salary;                  // 设置员工薪水
        this.hireDay = hireDay;                // 设置入职日期
        this.department = department;          // 设置所属部门
    }                                          // 构造函数结束

    /**
     * 覆写 toString() 方法，返回员工基本信息
     */
    public String toString() {                 // 覆写 Object 类的 toString() 方法
        return "id: " + id + "\n name:  " + name + " \n age: "    // 拼接编号、姓名、年龄
                        + age + "\n salary:  " + salary + "\n hireDay: "    // 拼接薪水、入职日期
                        + hireDay + "\n department: " + department ;        // 拼接部门信息
    }                                          // toString 方法结束

}                                              // EmployeeExtern 类结束

/**
 * ManagerExtern 类：继承 EmployeeExtern，实现 Externalizable 接口
 * Externalizable 要求实现类完全自定义序列化逻辑，框架不提供任何默认行为
 */
class ManagerExtern_mimofixed extends EmployeeExtern_mimofixed implements Externalizable {  // ManagerExtern 继承 EmployeeExtern 并实现 Externalizable
    String position;                          // 管理职位（子类新增字段）

    public ManagerExtern_mimofixed() {}                 // 默认无参构造方法（Externalizable 反序列化时必需）

    ManagerExtern_mimofixed(int id, String name, int age, int salary, String hireDay,   // 带参构造方法
                String department, String position) {                          // 增加了 position 参数
        super(id, name, age, salary, hireDay, department);  // 调用父类构造方法初始化继承的字段
        this.position = position;               // 设置职位
    }                                           // 构造函数结束

    /**
     * 实现 Externalizable 接口的 writeExternal 方法
     * 完全手动控制序列化：写入所有需要的字段（包括继承的父类字段）
     */
    public void writeExternal(ObjectOutput out) throws IOException {  // 外部化序列化方法（必须实现）
        Calendar cal = Calendar.getInstance();         // 获取当前日期时间

        out.writeInt(id);                        // 手动写入 id（继承自父类）
        out.writeInt(age);                       // 手动写入 age（继承自父类）
        out.writeObject(name);                   // 使用 writeObject 写入 name 字符串
        out.writeInt(salary);                    // 手动写入 salary（继承自父类）
        out.writeObject(hireDay);                // 使用 writeObject 写入 hireDay 字符串
        out.writeObject(department);             // 使用 writeObject 写入 department 字符串
        out.writeObject(position);               // 写入子类特有的 position 字段
        out.writeInt(cal.get(Calendar.YEAR));       // 额外写入当前年份（用于年龄自动更新），使用Calendar替代废弃的Date.getYear()

    }                                            // writeExternal 方法结束

    /**
     * 实现 Externalizable 接口的 readExternal 方法
     * 完全手动控制反序列化：按写入顺序读取所有字段
     */
    public void readExternal(ObjectInput in) throws IOException,   // 外部化反序列化方法（必须实现）
            java.lang.ClassNotFoundException {                     // 声明可能抛出的类未找到异常

        Calendar cal = Calendar.getInstance();         // 获取当前日期时间（反序列化时刻）
        int savedYear;                           // 声明变量存储序列化时保存的年份

        id = in.readInt();                       // 读取 id（必须与写入顺序一致）
        age = in.readInt();                      // 读取 age
        name = (String) in.readObject();         // 读取 name（readObject 返回 Object，需强制转换）
        salary = in.readInt();                   // 读取 salary
        hireDay = (String) in.readObject();      // 读取 hireDay
        department = (String) in.readObject();   // 读取 department
        position = (String) in.readObject();     // 读取 position
        savedYear = in.readInt();                // 读取保存的年份

        age = age + (cal.get(Calendar.YEAR) - savedYear);  // 自动更新年龄：原年龄 +（当前年份 - 保存年份），使用Calendar替代废弃的Date.getYear()
    }                                            // readExternal 方法结束

    /**
     * 覆写 toString() 方法，调用父类的 toString() 并追加职位信息
     */
    public String toString() {                   // 覆写 toString()
        return super.toString() + "\n position:  " + position;  // 调用父类的 toString() 拼接基本信息，再追加职位信息
    }                                            // toString 方法结束

}                                                // ManagerExtern 类结束

/**
 * 【功能说明】
 *   主程序类，演示 Externalizable 接口的对象序列化和反序列化：
 *   1. 创建一个 ManagerExtern 对象（包含继承的父类字段和子类特有字段）
 *   2. 通过 ObjectOutputStream 序列化到文件 data2.ser
 *   3. 从文件中反序列化恢复 ManagerExtern 对象
 *   4. 输出恢复后的经理信息（年龄根据年份差自动更新）
 *
 * 【知识点】
 *   1. Externalizable vs Serializable：Externalizable 需完全手写读写逻辑，Serializable 可默认或自定义部分逻辑。
 *   2. writeExternal / readExternal：Externalizable 接口的唯一两个方法，必须实现以完成自定义序列化。
 *   3. 无参构造必要性：Externalizable 反序列化时先通过无参构造创建对象，再调用 readExternal 填充数据。
 *   4. try-catch 异常处理：两次 IO 操作分别捕获并处理异常（此处直接打印异常信息）。
 *   5. 继承字段手动序列化：父类的字段不会自动序列化，需在 writeExternal/readExternal 中手动处理。
 *   6. 路径不一致问题：写入文件为 "src\\chp7_io\\exp7_11\\data2.ser"，读取为 "data2.ser"，
 *      运行时的当前工作目录决定了哪个路径能正常访问文件。
 */
public class ObjectTest_mimofixed {                    // 定义 ObjectTest 公有类（外部化序列化测试主程序）

    public static void main(String args[]) { // 程序入口 main 方法（此处未声明抛出异常，使用 try-catch 处理）

        // 创建 ManagerExtern 对象：经理 Jack，40 岁，薪水 10000，1980/10/10 入职，intel 部门，teamleader 职位
        ManagerExtern_mimofixed manager = new ManagerExtern_mimofixed(456789, "Jensen Hwang", 40, 1000000, "80/10/10",
                                                "Nvidia", "CEO");

        // ========== 第一部分：序列化 ManagerExtern 对象到文件 ==========
        try {                                // try 块开始，捕获序列化过程中的异常
            ObjectOutputStream fout = new ObjectOutputStream(       // 创建 ObjectOutputStream
                                            new FileOutputStream("java\\src\\chp7_io\\exp7_11\\data2.ser"));
            // 包装 FileOutputStream，输出路径包含包目录

            fout.writeObject(manager);          // 序列化 ManagerExtern 对象（自动调用 writeExternal 方法）
            fout.close();                       // 关闭输出流，释放资源

        } catch (Exception e) {                 // 捕获所有异常
            System.out.println(e);              // 直接将异常信息打印到控制台
        }                                       // try-catch 块结束

        // ========== 第二部分：反序列化恢复 ManagerExtern 对象 ==========
        manager = null;                         // 将原引用置空，便于垃圾回收
        ObjectInputStream fin = null;           // 声明ObjectInputStream引用，用于finally块中关闭资源

        try {                                   // try 块开始，捕获反序列化过程中的异常
            fin = new ObjectInputStream(          // 创建 ObjectInputStream
                                            new FileInputStream("java\\src\\chp7_io\\exp7_11\\data2.ser"));
            // 注意：反序列化路径为 "data2.ser"（相对根目录，与写入路径不同）

            manager = (ManagerExtern_mimofixed) fin.readObject();  // 反序列化恢复对象（自动调用 readExternal 方法）
        } catch (Exception e) {                 // 捕获所有异常
            System.out.println(e);              // 直接将异常信息打印到控制台
        } finally {                             // finally块：确保资源被关闭
            if (fin != null) {                  // 检查ObjectInputStream是否已成功创建
                try {
                    fin.close();                // 关闭ObjectInputStream，释放资源
                } catch (IOException e) {       // 捕获关闭时可能抛出的异常
                    System.out.println(e);      // 打印异常信息
                }
            }
        }                                       // try-catch-finally 块结束

        System.out.println("manager " + manager.toString());  // 输出反序列化恢复后的经理信息

    }                                           // main 方法结束

}                                               // ObjectTest 类结束
